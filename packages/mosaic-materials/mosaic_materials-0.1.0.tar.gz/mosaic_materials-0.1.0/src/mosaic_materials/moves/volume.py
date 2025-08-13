import numpy as np

from mosaic_materials.moves.move import MoveStrategy


class VolumeMove(MoveStrategy):
    """
    Propose Δ = δln(V) ∈ [-Δ, +Δ] so that V_new = V_old * exp(Δ).

    If `rigid_molecules=True`, move each molecule as a rigid body by scaling its
    COM with the box change and keeping internal coordinates fixed.
    """

    tuning_param = "max_dlnv"

    def __init__(
        self,
        engine,
        atom_ids: list[int] | None = None,
        max_dlnv: float = 1.0,
        rigid_molecules: bool = False,
        rng: np.random.Generator | None = None,
    ):
        # --- engine state ---
        self.engine = engine
        self.lmp = engine.lmp
        self.system = engine.system
        self.max_dlnv = max_dlnv
        self.rigid_molecules = rigid_molecules
        self.rng = rng or np.random.default_rng()

        # --- storage for acceptance criterion ---
        self._last_V_old = None
        self._last_delta = None

        # --- grab once the global atom‐ID list ---
        a_ids = self.system.all_atom_ids
        self._ids = a_ids
        n_atoms = a_ids.size

        # --- get each atom’s molecule tag and build an “inverse index” ---
        self._mol_ids = self.system.all_molecule_ids  # shape (M,)
        self._counts = self.system.molecule_counts    # shape (M,)
        self._inv = self.system.atom_molecule_index   # shape (N,)

        # --- scratch arrays ---
        self.hi_old = np.empty(3, np.float64)
        self.pos_old = np.empty((n_atoms, 3), np.float64)
        self.img_old = np.empty((n_atoms, 3), np.int32)
        self.pos_new = np.empty((n_atoms, 3), np.float64)
        self.img_new = np.empty((n_atoms, 3), np.int32)

        # --- per‐mol accumulator for coordinate sums ---
        self._sums = np.zeros((self._mol_ids.size, 3), np.float64)

    def propose(self) -> None:

        # --- old box & volume ---
        _, hi_old, *_ = self.lmp.extract_box()
        hi_old = np.array(hi_old)
        V_old = hi_old.prod()

        # --- remember for reject ---
        self.hi_old[:] = hi_old
        self._last_V_old = V_old

        # --- snapshot coords/images ---
        self.pos_old[:] = self.lmp.gather_atoms("x")
        self.img_old[:] = self.lmp.gather_atoms("image")

        # --- propose δlnV ---
        δ = self.rng.uniform(-self.max_dlnv, +self.max_dlnv)
        lam = np.exp(δ / 3)
        hi_new = hi_old * lam

        self._last_V_old = V_old
        self._last_delta = δ

        # --- change box in LAMMPS & system ---
        cmd = (
            f"change_box all "
            f"x final 0.0 {hi_new[0]:.6f} "
            f"y final 0.0 {hi_new[1]:.6f} "
            f"z final 0.0 {hi_new[2]:.6f} " +
            ("remap" if not self.rigid_molecules else "")
        )
        self.lmp.command(cmd)
        self.system.refresh_box(self.engine.units)

        if not self.rigid_molecules:
            return

        # --- COM‐preserving scaling ---
        abs_old = self.pos_old + self.img_old * hi_old
        self._sums[:] = 0.0
        np.add.at(self._sums, self._inv, abs_old)
        coms = self._sums / self._counts[:, None]
        com_atoms = coms[self._inv]
        abs_new = com_atoms * lam + (abs_old - com_atoms)
        quot, rem = np.divmod(abs_new, hi_new)
        self.img_new[:] = quot.astype(int)
        self.pos_new[:] = rem

        # --- push back into LAMMPS ---
        self.lmp.scatter_atoms("x", self.pos_new, ids=self._ids)
        self.lmp.scatter_atoms("image", self.img_new, ids=self._ids)

    def accept(self) -> None:
        pass

    def reject(self) -> None:
        # restore the old box.
        cmd = (
            f"change_box all "
            f"x final 0.0 {self.hi_old[0]:.6f} "
            f"y final 0.0 {self.hi_old[1]:.6f} "
            f"z final 0.0 {self.hi_old[2]:.6f} "
        )
        self.lmp.command(cmd)
        self.engine.system.refresh_box(self.engine.units)

        # restore coords/images
        aids = self.system.all_atom_ids
        self.lmp.scatter_atoms("x", self.pos_old, ids=aids)
        self.lmp.scatter_atoms("image", self.img_old, ids=aids)

    def jacobian_power(self) -> int:
        """Number of independent 3D points were scaled by the box move."""

        if self.rigid_molecules:
            return int(self.system.n_molecules)

        return int(self.system.n_atoms)
