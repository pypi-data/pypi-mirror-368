from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt
from numba import njit, prange

from mosaic_materials.constraints.constraint import Constraint
from mosaic_materials.constraints.rdf import RDFConstraint
from mosaic_materials.data.total_scattering import ScatteringData
from mosaic_materials.state import SimulationState

if TYPE_CHECKING:
    from mosaic_materials.engine import MCEngine


class StructureFactorConstraint(Constraint, ABC):
    """Base class for total-scattering constraints (e.g., X-ray, neutron).
    Subclasses must implement `_compute_scattering` to go from g(r) → S(Q)."""

    default_minimise_differences: bool = False
    """ Subclasses may override `default_minimise_differences` to set whether
    to perform the analytical scale minimisation by default. """

    def __init__(
        self,
        name: str,
        q_exp: np.ndarray,
        fq_exp: np.ndarray,
        rdf_constraint_name: str = "c_rdf",
        sigma: np.ndarray | float = 1.0,
        weight: float = 1.0,
        multiply_by_q: bool = False,
        minimise_differences: bool = False,
    ):
        """
        Parameters:
        ----------
        name
            Unique label for this dataset (also used as the key in
            state.scattering).
        q_exp
            Experimental Q-axis (1/Å).
        fq_exp
            Experimental S(Q) or F(Q) values.
        rdf_constraint_name
            The `name` of the RDFConstraint which must be run first.
        sigma
            Experimental uncertainty (same units as pattern_exp).
        weight
            Multiplicative weight on the χ² cost.
        multiply_by_q
            If True, multiply the computed S(Q) by Q before minimising.
        minimise_differences
            If True, apply analytical scaling to minimise the differences
            between the computed and experimental patterns. If False, compute 
            the raw χ².
        """

        super().__init__(weight=weight)

        self.name: str = name
        self.rdf_name: str = rdf_constraint_name
        self.q_exp: np.ndarray = q_exp
        self.fq_exp: np.ndarray = fq_exp
        self.sigma: np.ndarray | float = sigma
        self.multiply_by_q: bool = multiply_by_q
        self.minimise_differences: bool = minimise_differences

        self._rsum: npt.NDArray[np.floating] | None = None
        self._constants: npt.NDArray[np.floating] | None = None

    def install(self, engine: MCEngine) -> None:
        """
        Nothing to install in LAMMPS itself. We compute required constants.

        Parameters
        ----------
        engine
            The MCEngine instance, which must have a system set.
        """

        super().install(engine)

        rdf_c = next(
            c
            for c in engine._chi2_constraints
            if c.label() == self.rdf_name and isinstance(c, RDFConstraint)
        )

        assert rdf_c.installed and rdf_c._r_values is not None, (
            f"RDFConstraint `{self.rdf_name}` must be installed before "
            "StructureFactorConstraint."
        )

        self._rsum = fourier_rsum(self.q_exp, rdf_c._r_values).T

    def compute(self, state: SimulationState) -> float:
        """
        1) Ensure the RDF is in the state (running the RDFConstraint if needed).
        2) Call _compute_partials(gr) → array shape (n_pairs, n_Q).
        3) Sum axis=0 to get total S(Q).
        4) Compute χ² vs. the experimental pattern self.fq_exp.
        5) Cache both partials and total in state.scattering_partials and
           state.scattering dictionaries.
        6) Return weighted χ² (weighted by 1.0 by default).

        Parameters
        ----------
        state
            The current simulation state, which must contain the RDF.
        """

        # --- 1) ensure g(r) is present ---
        if state.rdf is None or self.rdf_name not in state.rdf:
            rdf_c = next(
                c
                for c in self.engine._chi2_constraints  # type: ignore
                if isinstance(c, RDFConstraint) and c.label() == self.rdf_name
            )
            rdf_c.compute(state)

        gr = state.rdf[self.rdf_name]

        # --- 2) compute partial structure factors S_ij(Q) ---
        partials = self._compute_partials(gr)  # shape (n_pairs, n_Q)

        # --- 3a) sum to get total pattern S(Q) ---
        total_fq = partials.sum(axis=0)  # shape (n_Q,)

        # --- 3b) multiply by Q if requested ---
        if self.multiply_by_q:
            total_fq *= self.q_exp

        # --- 3c) minimise differences if requested ---
        if self.minimise_differences:
            total_fq = minimise_difference(total_fq, self.fq_exp)

        # --- 4) χ² against experimental pattern ---
        chi2 = np.sum((total_fq - self.fq_exp) ** 2 / self.sigma**2)

        # --- 5) cache in state ---
        if state.scattering_partials is None:
            state.scattering_partials = {}
        state.scattering_partials[self.name] = partials

        if state.scattering is None:
            state.scattering = {}
        state.scattering[self.name] = total_fq

        # --- 6) return weighted cost ---
        return float(self.weight * chi2)

    def _compute_partials(
        self,
        gr: np.ndarray,
    ) -> npt.NDArray[np.floating]:
        """
        Compute the partial S_ij(Q) for each element‐pair at self.q_exp.
        Returns an array of shape (n_pairs, len(self.q_exp)).

        Parameters
        ----------
        gr
            The g(r) array from the RDFConstraint, shape (n_pairs, n_bins).
        """

        assert self.engine is not None, "install() must be called first"
        assert self._rsum is not None, "install() must set _rsum"
        assert self._constants is not None, "install() must set _constants"

        rho0 = self.engine.system.atomic_number_density

        diffs = gr - 1.0             # (n_pairs, n_bins)
        raw = diffs.dot(self._rsum)  # (n_pairs, n_Q)
        return raw * self._constants[:, None] * rho0 

    def label(self) -> str:
        return self.name

    @classmethod
    def from_scattering_data(
        cls,
        name: str,
        scattering: ScatteringData,
        rdf_constraint_name: str = "c_rdf",
        minimise_differences: bool | None = None,
        weight: float = 1.0,
    ) -> StructureFactorConstraint:
        """
        Factory constructor using a ScatteringData object.

        Parameters
        ----------
        name
            Label for this constraint.
        rdf_constraint_name
            Name of the RDFConstraint to source g(r).
        scattering
            Already-loaded experimental data with weights and flags.
        minimise_differences
            Override whether to apply analytical scaling to minimise χ².
            If None, uses the class's `default_minimise_differences`.
        """

        md = (
            minimise_differences
            if minimise_differences is not None
            else cls.default_minimise_differences
        )
        return cls(
            name=name,
            rdf_constraint_name=rdf_constraint_name,
            q_exp=scattering.x,
            fq_exp=scattering.y,
            sigma=scattering.sigmas,
            weight=weight,
            multiply_by_q=scattering.multiply_q,
            minimise_differences=md,
        )


# === Helper functions ===

def fourier_rsum(
    q_values: np.ndarray,
    r_values: np.ndarray,
) -> npt.NDArray[np.floating]:
    """
    Calculation of

        r^2 * dr * sin(Q*r) / (Q*r)

    for all Q in `qs` and r in `rs`.
    """

    dr = np.gradient(r_values)  # shape (n_r,)
    r2dr = r_values**2 * dr  # shape (n_r,)
    qr = np.outer(q_values, r_values)  # shape (n_q, n_r)
    kernel = np.sinc(qr / np.pi)  # shape (n_q, n_r)
    return kernel * r2dr  # shape (n_q, n_r)


@njit(parallel=True, fastmath=True)
def minimise_difference(calc: np.ndarray, expt: np.ndarray) -> np.ndarray:
    """
    Scale `calc` by the factor s that minimises

        χ² = Σ_i[s*calc_i - expt_i]²

    s = (calc·expt) / (calc·calc)

    Returns
    -------
    The scaled array `s * calc`.
    """

    n = calc.shape[0]
    dot_cb = 0.0
    dot_cc = 0.0

    for i in range(n):
        ci = calc[i]
        dot_cb += ci * expt[i]
        dot_cc += ci * ci

    if dot_cc == 0.0:
        return np.zeros(n, dtype=calc.dtype)

    s = dot_cb / dot_cc
    out = np.empty(n, dtype=calc.dtype)
    for i in prange(n):
        out[i] = calc[i] * s

    return out
