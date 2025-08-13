from abc import ABC, abstractmethod

import numpy as np


class MoveStrategy(ABC):
    """Abstract base class for MC move strategies."""

    @abstractmethod
    def propose(self) -> None:
        """Make a trial change, and send it into LAMMPS."""
        ...

    @abstractmethod
    def accept(self) -> None:
        """Called *after* a move is accepted; e.g. to refresh the box."""
        ...

    @abstractmethod
    def reject(self) -> None:
        """Revert LAMMPS back to the original state."""
        ...


class BaseMove(MoveStrategy):
    """
    Tracks an “old” and a “new” configuration for a set of atoms,
    and knows how to push either into LAMMPS.
    """

    def __init__(
        self,
        engine,
        atom_ids: list[int],
        rng: np.random.Generator | None = None,
    ):
        self.engine = engine
        self.lmp = engine.lmp
        self.system = engine.system
        self.atom_ids = np.asarray(atom_ids, dtype=int)
        self.rng = rng or np.random.default_rng()

        # --- gather the “old” coords + image flags once ---
        self.pos_old: np.ndarray = self.lmp.gather_atoms(
            "x", ids=self.atom_ids
        )  # shape (n,3)

        self.img_old: np.ndarray = self.lmp.gather_atoms(
            "image", ids=self.atom_ids
        )  # shape (n,3)

        # --- initialize the “new” to a copy of the old ---
        self.pos_new = self.pos_old.copy()
        self.img_new = self.img_old.copy()

    def _apply(self) -> None:
        """Send pos_new/img_new into LAMMPS in one place."""

        self.lmp.scatter_atoms("x", self.pos_new, ids=self.atom_ids)
        self.lmp.scatter_atoms("image", self.img_new, ids=self.atom_ids)

    def accept(self) -> None:
        """By default, nothing special to do on accept."""
        pass

    def reject(self) -> None:
        """Restore the original coordinates/images."""

        self.lmp.scatter_atoms("x", self.pos_old, ids=self.atom_ids)
        self.lmp.scatter_atoms("image", self.img_old, ids=self.atom_ids)
