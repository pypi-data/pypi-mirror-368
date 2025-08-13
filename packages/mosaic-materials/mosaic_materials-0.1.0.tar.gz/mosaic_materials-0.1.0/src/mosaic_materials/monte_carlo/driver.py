from __future__ import annotations

from typing import Final, Sequence

import numpy as np
from ase.units import kB

from mosaic_materials.monte_carlo.adapt import MoveSpec
from mosaic_materials.monte_carlo.callbacks import DriverCallback
from mosaic_materials.monte_carlo.criteria import npt_accept, nvt_accept
from mosaic_materials.monte_carlo.schedules import Schedule
from mosaic_materials.state import SimulationState

MIN_TEMPERATURE: Final[float] = 1e-9  # K


class MCDriver:
    """
    An “adaptive” Metropolis driver:
      - Drives NVT (or NPT, if pressure_schedule provided)
      - Tunes each MoveSpec's tuning parameter to hit its target acceptance
      - Applies temperature/pressure schedules
    """

    def __init__(
        self,
        engine,
        move_specs: list[MoveSpec],
        temperature_schedule: Schedule,
        pressure_schedule: Schedule | None = None,
        callbacks: Sequence[DriverCallback] = (),
    ):
        # --- engine state ---
        self.engine = engine
        self.system = engine.system
        self.rng = engine.rng

        # --- available moves ---
        self.move_specs = list(move_specs)

        # --- schedules ---
        self.temperature_schedule = temperature_schedule
        self.pressure_schedule = pressure_schedule

        # --- enthalpy constraint ---
        self._enthalpy_c = engine._enthalpy_constraint

        # --- callbacks ---
        self.callbacks: list[DriverCallback] = list(callbacks)

        # --- public-at-a-glance values for logging/callbacks ---
        self.temperature: float = np.nan
        self.beta: float = np.nan
        self.pressure: float | None = None

        # --- initial MC state ---
        self.state = SimulationState()
        self._chi2 = self._compute_chi2(self.state)
        self._U = (
            self._enthalpy_c.compute(self.state) if self._enthalpy_c else 0.0
        )
        self._V = np.prod(self.system.cell_lengths)

    def register_callback(self, cb: DriverCallback) -> None:
        """Add another function to be called every step."""

        self.callbacks.append(cb)

    def _compute_chi2(self, state: SimulationState) -> float:
        """Sum χ² over all non-enthalpy constraints."""

        total = 0.0
        state.costs.clear()
        for c in self.engine._chi2_constraints:
            val = c.compute(state)
            state.costs[c.label()] = float(val)
            total += val
        return total

    def _update_thermo_controls(self, step: int) -> None:
        """Update temperature and pressure based on the current step."""

        T = max(self.temperature_schedule.value(step), MIN_TEMPERATURE)
        beta = 1.0 / (kB * T)

        self.temperature = T
        self.beta = beta

        if self._enthalpy_c:
            self._enthalpy_c.update_temperature(T)

        self.pressure = (
            self.pressure_schedule.value(step)
            if self.pressure_schedule
            else None
        )

    def run(self, n_steps: int):
        """Run `n_steps` of MC."""

        for step in range(1, n_steps + 1):
            # --- update T & P (if applicable) ---
            self._update_thermo_controls(step)

            # --- pick & instantiate a move ---
            spec: MoveSpec = self.rng.choice(self.move_specs)
            move = spec.instantiate(self.engine, self.rng)

            # --- snapshot old MC stats ---
            χ2_old = self._chi2
            U_old = self._U
            V_old = self._V

            # --- propose ---
            move.propose()
            self.engine.lmp.command("run 1 post no")

            # --- compute on a scratch state (trial only) ---
            trial_state = SimulationState()
            χ2_new = self._compute_chi2(trial_state)

            U_new = (
                self._enthalpy_c.compute(trial_state)
                if self._enthalpy_c
                else 0.0
            )
            if self._enthalpy_c:
                trial_state.costs[self._enthalpy_c.label()] = float(U_new)

            V_new = float(self.engine.lmp.get_thermo("vol"))

            # --- decide acceptance (NVT or NPT) ---
            if self.pressure is None:
                accept = nvt_accept(
                    U_old,
                    U_new,
                    self.beta,
                    chi2_old=χ2_old,
                    chi2_new=χ2_new,
                    rng=self.rng,
                )
            else:
                N = self.system.all_atom_ids.size
                accept = npt_accept(
                    U_old,
                    U_new,
                    V_old,
                    V_new,
                    N,
                    self.beta,
                    self.pressure,
                    chi2_old=χ2_old,
                    chi2_new=χ2_new,
                    rng=self.rng,
                )

            #  --- commit new state if accepted ---
            if accept:

                # commit new MC stats
                self._chi2 = χ2_new
                self._U = U_new
                self._V = V_new

                self.state = trial_state
                if hasattr(move, "accept"):
                    move.accept()

                spec.record(True)
            else:
                move.reject()
                spec.record(False)

            # --- call all callbacks ---
            for cb in self.callbacks:
                cb(self, step, spec, accept, self._chi2, self._U, self._V)

            yield step, spec.name, accept, self._chi2, self._U, self._V
