import numpy as np

from mosaic_materials.moves.move import BaseMove
from mosaic_materials.moves.utils import random_vector


class TranslateMove(BaseMove):
    """
    Translate the chosen atoms by a small random vector.
    """

    tuning_param = "max_disp"

    def __init__(
        self,
        engine,
        atom_ids: list[int],
        max_disp: float,
        rng: np.random.Generator | None = None,
    ):
        super().__init__(engine, atom_ids, rng)
        self.max_disp = max_disp

    def propose(self) -> None:
        # --- random direction & magnitude in [0, max_disp] ---
        direction = random_vector(self.rng.random(), self.rng.random())
        length = self.max_disp * self.rng.random()
        disp = direction * length

        # --- apply to old positions → get unwrapped Cartesian coords ---
        cart_old = self.pos_old + self.img_old * self.system.cell_lengths

        # --- compute new unwrapped coords, then re-wrap into box [0,L) ---
        cart_new = cart_old + disp
        img_new = np.floor_divide(cart_new, self.system.cell_lengths).astype(
            int
        )
        pos_new = cart_new - img_new * self.system.cell_lengths

        # --- store & send ---
        self.pos_new = pos_new
        self.img_new = img_new
        self._apply()
