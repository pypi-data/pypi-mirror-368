from __future__ import annotations

import contextlib
import weakref
from pathlib import Path

import ase
import numpy as np
from ase.calculators.lammps import Prism
from pylammpsmpi import LammpsLibrary

from mosaic_materials.constraints import Constraint, EnthalpyConstraint
from mosaic_materials.state.styles import (
    DEFAULT_ATOM_STYLE,
    DEFAULT_BOUNDARY,
    DEFAULT_UNITS,
    AtomStyle,
    Boundary,
    BoundaryInput,
    UnitStyle,
    boundary_str,
    normalise_boundary,
    validate_atom_style,
    validate_unit_style,
)
from mosaic_materials.state.system import (
    System,
    get_atom_types_from_ase,
    get_lammps_cell,
    set_lammps_masses,
    set_lammps_prism,
)


class MCEngine:

    _units: UnitStyle
    _boundary: Boundary
    _atom_style: AtomStyle

    def __init__(
        self,
        cores: int = 1,
        units: UnitStyle = DEFAULT_UNITS,
        boundary: BoundaryInput = DEFAULT_BOUNDARY,
        atom_style: AtomStyle = DEFAULT_ATOM_STYLE,
        mode: str = "local",
        seed: int | None = None,
    ):
        # --- LAMPS backend ---
        self.lmp = LammpsLibrary(cores=cores, mode=mode)
        self._closed = False
        self._finaliser = weakref.finalize(self, self._unsafe_close)

        # --- random number generator for moves ---
        self.rng = np.random.default_rng(seed)

        # --- simulation settings ---
        self.units = units
        self.boundary = boundary
        self.atom_style = atom_style

        # --- bookkeeping ---
        self._compute_ids: set[str] = set()
        self._enthalpy_constraint: EnthalpyConstraint | None = None
        self._chi2_constraints: list[Constraint] = []
        self.system = None
        self._needs_compute = True

    # --- properties for units / boundary / atom style ---

    @property
    def units(self) -> UnitStyle:
        return self._units

    @units.setter
    def units(self, u: UnitStyle):
        u = validate_unit_style(u)
        self._units = u
        self.lmp.command(f"units {u}")

    @property
    def boundary(self) -> Boundary:
        return self._boundary

    @boundary.setter
    def boundary(self, b: BoundaryInput):
        norm = normalise_boundary(b)
        self._boundary = norm
        self.lmp.command(f"boundary {boundary_str(norm)}")

    @property
    def atom_style(self) -> AtomStyle:
        return self._atom_style

    @atom_style.setter
    def atom_style(self, style: AtomStyle):
        style = validate_atom_style(style)
        self._atom_style = style
        self.lmp.command(f"atom_style {style}")

    # --- constraint properties ---

    @property
    def enthalpy_constraint(self) -> EnthalpyConstraint | None:
        """Return the registered enthalpy constraint, if any."""

        return self._enthalpy_constraint

    @property
    def chi2_constraints(self) -> tuple[Constraint, ...]:
        """Return a tuple of all registered chi2 constraints."""

        return tuple(self._chi2_constraints)

    # --- system initialisation from data or ASE ---

    def load_lammps_data(
        self, data_file: str | Path, atom_types: dict[int, str] | None = None
    ) -> None:
        """Read a LAMMPS data file into the engine."""

        if isinstance(data_file, Path):
            data_file = str(data_file)

        if not data_file.endswith(".data"):
            raise ValueError(
                "Expected a LAMMPS data file with '.data' extension, "
                f"got: {data_file}"
            )

        if not Path(data_file).is_file():
            raise FileNotFoundError(f"Data file not found: {data_file}")

        self.lmp.command(f"read_data {data_file}")
        self.system = System(self.lmp, self.units, atom_types)

    def load_ase_atoms(self, atoms: ase.Atoms) -> None:
        """Add atoms from an ASE Atoms object to the engine."""

        if not isinstance(atoms, ase.Atoms):
            raise TypeError("Expected an ASE Atoms object.")

        prism = Prism(atoms.cell.array)
        atom_types, all_atom_types = get_atom_types_from_ase(atoms)
        positions = prism.vector_to_lammps(atoms.positions).flatten()

        set_lammps_prism(self.lmp, prism)
        self.lmp.command(f"create_box {len(atom_types)} 1")
        set_lammps_masses(self.lmp, atom_types)

        self.lmp.create_atoms(
            n=len(atoms),
            id=range(1, len(atoms) + 1),
            type=all_atom_types,
            x=positions,
            v=None,
            image=None,
            shrinkexceed=False,
        )

        if "mol-id" in atoms.arrays:
            mol_ids = atoms.arrays["mol-id"]
            if len(mol_ids) != len(atoms):
                raise ValueError(
                    "Length of 'mol-id' array does not match number of atoms."
                )
            self.lmp.scatter_atoms("molecule", mol_ids)

        self.lmp.command("change_box all remap")

        self.system = System(self.lmp, self.units, atom_types=atom_types)

        if "mol-id" in atoms.arrays:
            self.system.unwrap()

    def to_ase_atoms(self) -> ase.Atoms:
        """Convert the current state to ASE Atoms object."""

        if self.system is None:
            raise RuntimeError(
                "No system loaded. Use `load_lammps_data` or `load_ase_atoms` "
                "first."
            )

        # 1) get LAMMPS cell.
        cell = get_lammps_cell(self.lmp, self.units)

        # 2) gather per‐atom arrays from LAMMPS
        atom_types = self.lmp.gather_atoms("type")
        positions = self.system.prism.vector_to_ase(self.lmp.gather_atoms("x"))
        molecule_ids = self.lmp.gather_atoms("molecule")

        # 3) map types → symbols
        symbols = [self.system.atom_types[i] for i in atom_types]

        # 4) create ASE Atoms object.
        atoms = ase.Atoms(
            symbols=symbols,
            positions=positions,
            cell=cell,
            pbc=True,
        )
        atoms.info["mol-id"] = molecule_ids

        return atoms

    # --- force field and constraint registration  ---

    def add_force_field(self, style: str, coeffs: list[str] | str) -> None:
        """Add a force field to the engine."""

        if isinstance(coeffs, str):
            coeffs = [coeffs]

        self.lmp.command(f"pair_style {style}")

        for coeff in coeffs:
            self.lmp.command(f"pair_coeff {coeff}")

    def add_constraint(self, constraint: Constraint) -> None:
        """Add a constraint to the engine."""

        if self.system is None:
            raise RuntimeError("Load a system before adding constraints.")

        name = constraint.label()
        if isinstance(constraint, EnthalpyConstraint):
            if self._enthalpy_constraint is not None:
                raise RuntimeError("Only one EnthalpyConstraint allowed")
            constraint.install(self)
            self._enthalpy_constraint = constraint
        else:
            if any(c.label() == name for c in self._chi2_constraints):
                raise RuntimeError(f"Constraint '{name}' already registered")
            constraint.install(self)
            self._chi2_constraints.append(constraint)

    def get_constraint(self, label: str) -> Constraint | None:
        """Retrieve a constraint by its label."""

        if (
            self._enthalpy_constraint
            and self._enthalpy_constraint.label() == label
        ):
            return self._enthalpy_constraint

        for c in self._chi2_constraints:
            if c.label() == label:
                return c

        return None

    def remove_constraint(self, label: str) -> None:
        """Remove a constraint by its label."""

        if (
            self._enthalpy_constraint
            and self._enthalpy_constraint.label() == label
        ):
            self._enthalpy_constraint.teardown()
            self._enthalpy_constraint = None
            return

        for i, c in enumerate(self._chi2_constraints):
            if c.label() == label:
                c.teardown()
                del self._chi2_constraints[i]
                return

        raise KeyError(f"No constraint named {label!r}")

    def register_compute(self, cid: str) -> None:
        """Called by a constraint to claim a compute ID."""

        if cid in self._compute_ids:
            raise RuntimeError(f"Compute ID '{cid}' is already in use")

        self._compute_ids.add(cid)

    def unregister_compute(self, cid: str) -> None:
        """Free up a compute ID when a constraint is torn down."""

        self._compute_ids.discard(cid)

    # --- simulation control ---

    def close(self) -> None:
        """Cleanly shut down the LAMMPS instance."""

        if self._closed:
            return

        if self._enthalpy_constraint is not None:
            self._enthalpy_constraint.teardown()

        for c in list(self._chi2_constraints):
            c.teardown()

        with contextlib.suppress(Exception):
            self.lmp.close()

        self._closed = True
        self._finaliser.detach()

    def _unsafe_close(self):
        """Used by finaliser; best-effort cleanup without raising."""

        with contextlib.suppress(Exception):
            self.lmp.shutdown()

    def __enter__(self) -> MCEngine:
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
