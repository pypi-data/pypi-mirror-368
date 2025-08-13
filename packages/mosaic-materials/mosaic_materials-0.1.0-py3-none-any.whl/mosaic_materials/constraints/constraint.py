from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from mosaic_materials.state import SimulationState

# === Base Constraint class ===


class Constraint(ABC):
    def __init__(self, weight: float = 1.0):
        self.weight = weight
        self.engine = None
        self.installed = False

    def install(self, engine) -> None:
        """
        Called once when the constraint is added to the engine.
        Gives you a chance to stash engine/system and
        send any one-time LAMMPS commands (e.g. compute/fix).
        """
        self.engine = engine
        self.installed = True

    @abstractmethod
    def compute(self, state: SimulationState) -> float:
        """Return weighted cost contribution."""
        ...

    @abstractmethod
    def label(self) -> str: ...

    def teardown(self) -> None:
        """
        Called once when the engine is closed or the constraint is removed.
        Here we should undo any LAMMPS commands installed in `install()`.
        """
        self.installed = False
        return

    def dump(self, state: SimulationState, output_dir: Path):
        """Optional artifact dump."""
        return

    def __del__(self):
        """Ensure teardown is called when the constraint is deleted."""

        self.teardown()
        self.engine = None
