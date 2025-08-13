from __future__ import annotations

from ase.units import kB

from mosaic_materials.constraints import Constraint
from mosaic_materials.state import SimulationState


class EnthalpyConstraint(Constraint):
    def __init__(self, temperature_Kelvin: float, weight: float = 1.0):
        super().__init__(weight=weight)
        self.e_constant = 1 / (kB * temperature_Kelvin)

    def compute(self, state: SimulationState) -> float:
        return self.engine.lmp.get_thermo("pe") * self.e_constant  # type: ignore[no-any-return]

    def label(self):
        return "c_enthalpy"

    def update_temperature(self, temperature_Kelvin: float):
        self.e_constant = 1 / (kB * temperature_Kelvin)
