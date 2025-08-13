import numpy as np

from mosaic_materials.moves.move import BaseMove
from mosaic_materials.moves.utils import _rotate_cluster_inplace, random_vector


class RotateMove(BaseMove):
    """
    Rotate a cluster of atoms about its center-of-mass by a random angle.
    """

    tuning_param = "max_angle"

    def __init__(
        self,
        engine,
        atom_ids: list[int],
        max_angle: float,
        rng: np.random.Generator | None = None,
    ):
        super().__init__(engine, atom_ids, rng)
        self.max_angle = max_angle

    def propose(self) -> None:
        # --- random axis & angle ---
        L = self.system.cell_lengths
        axis = random_vector(self.rng.random(), self.rng.random())
        theta = np.deg2rad(self.rng.uniform(-self.max_angle, self.max_angle))

        # --- perform the rotation ---
        _rotate_cluster_inplace(
            self.pos_old,
            self.img_old,
            L,
            axis,
            theta,
            self.pos_new,
            self.img_new,
        )
        self._apply()
