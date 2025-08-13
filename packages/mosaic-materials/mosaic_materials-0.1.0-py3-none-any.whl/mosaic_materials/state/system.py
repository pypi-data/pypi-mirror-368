from __future__ import annotations

import bisect
import warnings
from functools import cached_property
from typing import Any, Iterable

import ase
import numpy as np
import numpy.typing as npt
from ase.calculators.lammps import Prism, convert
from ase.data import atomic_masses, atomic_numbers, chemical_symbols
from pylammpsmpi import LammpsLibrary

from mosaic_materials.state.composition import Composition
from mosaic_materials.state.styles import UnitStyle


class System:
    """Holds main system information."""

    def __init__(
        self,
        lmp: LammpsLibrary,
        units: UnitStyle,
        atom_types: dict[int, str] | None = None,
    ):
        self.lmp = lmp

        self.cell = get_lammps_cell(lmp, units)
        self.prism = Prism(self.cell)

        self.atom_types = (
            atom_types
            if atom_types is not None
            else infer_symbols_from_masses(lmp)
        )
        (
            self._type_groups,
            self._elements,
            self._element_pairs,
            self._element_pair_patterns,
        ) = sort_atom_types(self.atom_types)

        self.composition = get_atomic_fractions(lmp, self.atom_types)

    def fractional_coordinates(
        self, cartesian_coords: npt.NDArray[np.floating]
    ) -> npt.NDArray[np.floating]:
        """Convert cartesian coordinates to fractional coordinates."""

        return np.linalg.solve(self.cell.T, np.transpose(cartesian_coords)).T

    def cartesian_coordinates(
        self, fractional_coords: npt.NDArray[np.floating]
    ) -> npt.NDArray[np.floating]:
        """Convert fractional coordinates to cartesian coordinates."""

        return fractional_coords @ self.cell

    def atoms_in_molecule(self, mol_id: int) -> npt.NDArray[np.int_]:
        """Return the LAMMPS atom IDs that have molecule‐tag == mol_id."""

        try:
            return self._molecule_atom_map[mol_id]
        except KeyError:
            raise ValueError(
                f"No atoms found for molecule ID {mol_id!r}"
            ) from None

    def pick_random_atom(self, rng: np.random.Generator | None = None) -> int:
        """Pick a single random atom ID."""

        rng = rng or np.random.default_rng()
        return int(rng.choice(self.all_atom_ids))

    def pick_random_molecule(
        self, rng: np.random.Generator | None = None
    ) -> tuple[int, npt.NDArray[np.int_]]:
        """Pick one molecule-ID at random, and return (mol_id, atom_ids).

        - mol_id: the chosen molecule tag (1-based)
        - atom_ids: the array of LAMMPS atom IDs belonging to that molecule
        """

        rng = rng or np.random.default_rng()
        mols = self.all_molecule_ids
        if mols.size == 0:
            raise ValueError("No molecules present in the system.")

        mol = int(rng.choice(mols))
        atom_ids = self.atoms_in_molecule(mol)

        return mol, atom_ids

    def refresh_box(self, units: UnitStyle) -> None:
        """Reload the box vectors from LAMMPS and rebuild any geometry-
        dependent cached properties."""

        self.cell = get_lammps_cell(self.lmp, units)
        self.prism = Prism(self.cell)

    def unwrap(self) -> None:
        """For every molecule in the box, shift all its atoms so that they lie
        in a single periodic image.  Writes the new coordinates and image flags
        back into LAMMPS, so that the simulation starts in a fully “unwrapped”
        state."""

        L = self.cell_lengths

        for atom_ids in self._molecule_atom_map.values():
            pos = self.lmp.gather_atoms("x", ids=atom_ids)
            img = self.lmp.gather_atoms("image", ids=atom_ids)

            abs_pos = pos + img * L[np.newaxis, :]
            ref = abs_pos[0]

            # compute how many box‐shifts each atom is away from ref.
            delta = abs_pos - ref[np.newaxis, :]
            shifts = np.rint(delta / L[np.newaxis, :]).astype(int)

            # subtract off those shifts
            abs_unwrapped = abs_pos - shifts * L[np.newaxis, :]

            # get periodic images & fractional positions in new box
            img_new = img - shifts
            pos_new = abs_unwrapped % L[np.newaxis, :]

            # send into LAMMPS
            self.lmp.scatter_atoms("x", pos_new, ids=atom_ids)
            self.lmp.scatter_atoms("image", img_new, ids=atom_ids)

    @property
    def volume(self) -> float:
        """Get the volume of the simulation box."""

        return self.lmp.get_thermo("vol")

    @property
    def atomic_number_density(self) -> float:
        """Get the atomic number density (atom/Å3)."""

        return self.composition.natoms / self.volume

    @property
    def cell_lengths(self) -> npt.NDArray[np.floating]:
        """Get the lengths of the simulation box."""

        return np.linalg.norm(self.cell, axis=1)

    @property
    def type_groups(self) -> dict[str, dict[str, Any]]:
        """Get type groups mapping symbols to type IDs and patterns."""

        return self._type_groups

    @property
    def elements(self) -> tuple[str, ...]:
        """Get sorted tuple of element symbols."""

        return self._elements

    @property
    def element_pairs(self) -> list[tuple[str, str]]:
        """Get list of unique element pairs."""

        return self._element_pairs

    @property
    def element_pair_patterns(self) -> list[tuple[str, str]]:
        """Get list of LAMMPS-style patterns for element pairs."""

        return self._element_pair_patterns

    @cached_property
    def all_atom_ids(self) -> npt.NDArray[np.int_]:
        """Return the raw LAMMPS atom IDs in this replica (1-based)."""

        return self.lmp.gather_atoms("id")

    @cached_property
    def all_molecule_ids(self) -> npt.NDArray[np.int64]:
        """Return the unique molecule tags present in the box."""

        mol_tags = self.lmp.gather_atoms("molecule")
        return np.unique(mol_tags).astype(np.int64)

    @cached_property
    def molecule_tags(self) -> np.ndarray:
        """Raw per-atom molecule-tag array, aligned with `all_atom_ids`."""

        return self.lmp.gather_atoms("molecule").astype(int)

    @cached_property
    def molecule_index(self) -> dict[int, int]:
        """Map each molecule-tag → its index in `all_molecule_ids`."""
        return {m: i for i, m in enumerate(self.all_molecule_ids)}

    @cached_property
    def atom_molecule_index(self) -> np.ndarray:
        """For each atom in `all_atom_ids`, gives the 0-based index of its
        molecule in `all_molecule_ids`.  Handy for doing group accumulations
        with np.add.at."""

        inv = np.empty_like(self.molecule_tags)
        for i, tag in enumerate(self.molecule_tags):
            inv[i] = self.molecule_index[int(tag)]
        return inv

    @cached_property
    def molecule_counts(self) -> np.ndarray:
        """Number of atoms per molecule, in the same order as
        `all_molecule_ids`."""

        _, counts = np.unique(self.molecule_tags, return_counts=True)
        return counts

    @cached_property
    def _molecule_atom_map(self) -> dict[int, np.ndarray]:
        """
        Build once a mapping {mol_id: array-of-atom-ids} from the LAMMPS
        per-atom molecule tags.
        """

        mol_tags = self.lmp.gather_atoms("molecule")
        atom_ids = self.lmp.gather_atoms("id")
        d: dict[int, list[int]] = {}

        for tag, aid in zip(mol_tags, atom_ids):
            tag = int(tag)
            d.setdefault(tag, []).append(int(aid))

        return {mol: np.array(aids, dtype=int) for mol, aids in d.items()}

    def _invalidate_caches(self):
        for attr in ("all_atom_ids", "all_molecule_ids", "_molecule_atom_map"):
            self.__dict__.pop(attr, None)


# === extraction functions ===


def infer_masses(
    lmp: LammpsLibrary,
) -> dict[int, float]:
    """Infer masses from atom types."""

    atom_types = np.unique(lmp.gather_atoms("type"))
    masses_arr = lmp.extract_atom("mass")
    atom_type_masses = {int(i): float(masses_arr[i]) for i in atom_types}

    return atom_type_masses


def get_lammps_cell(
    lmp: LammpsLibrary, units: UnitStyle
) -> npt.NDArray[np.floating]:
    """Get the simulation box from LAMMPS."""

    boxlo, boxhi, xy, xz, yz, *_ = lmp.extract_box()
    Lx, Ly, Lz = np.array(boxhi) - np.array(boxlo)

    cell = np.array(
        [
            [Lx, 0.0, 0.0],
            [xy, Ly, 0.0],
            [xz, yz, Lz],
        ]
    )

    return convert(cell, "distance", units, "ASE")


def infer_symbols_from_masses(
    lmp: LammpsLibrary, tol: float = 0.2, warn_tol: float = 0.05
) -> dict[int, str]:
    """
    Infer element symbols from the LAMMPS mass array.

    Parameters:
    ----------
    lmp
        A pylammpsmpi LAMMPS instance.
    tol
        Maximum allowed mass-difference (amu) before an error is raised.
    warn_tol
        If best-match difference is > warn_tol but <= tol, emit a warning.
    """

    atom_type_masses = infer_masses(lmp)
    symbol_map: dict[int, str] = {}

    for t, mass in atom_type_masses.items():
        idx = bisect.bisect_left(atomic_masses, mass)

        candidates = []
        if idx > 0:
            i = idx - 1
            candidates.append((atomic_masses[i], chemical_symbols[i]))
        if idx < len(atomic_masses):
            i = idx
            candidates.append((atomic_masses[i], chemical_symbols[i]))

        best_mass, best_sym = min(
            candidates, key=lambda pair: abs(pair[0] - mass)
        )
        diff = abs(best_mass - mass)

        if diff > tol:
            raise ValueError(
                f"Type {t}: measured mass={mass:.4f} amu, "
                f"closest match {best_sym} has {best_mass:.4f} amu "
                f"(Δ={diff:.4f} amu) > tol={tol}"
            )
        elif diff > warn_tol:
            warnings.warn(
                f"Type {t}: mass={mass:.4f} amu ↔ {best_sym} ({best_mass:.4f} "
                f"amu), Δ={diff:.4f} amu",
                UserWarning,
                stacklevel=2,
            )

        symbol_map[t] = best_sym

    return symbol_map


def get_molecules(lmp: LammpsLibrary) -> npt.NDArray:
    """Gather atom IDs grouped by their molecule IDs."""

    # 1. gather molecule IDs and atom IDs from LAMMPS.
    ids_m = lmp.gather_atoms("molecule")
    ids_a = lmp.gather_atoms("id")

    # 2. sort by molecule id so same-molecule atoms are contiguous.
    order = np.argsort(ids_m)
    sorted_mols = ids_m[order]
    sorted_ids = ids_a[order]

    # 3. find boundaries where molecule id changes.
    changes = np.nonzero(
        np.concatenate(([True], sorted_mols[1:] != sorted_mols[:-1], [True]))
    )[0]

    # 4. slice out atom IDs per molecule.
    mols = [
        sorted_ids[changes[i] : changes[i + 1]] for i in range(len(changes) - 1)
    ]

    return np.array(mols, dtype=object)


def get_atomic_fractions(
    lmp: LammpsLibrary,
    atom_type_symbols: dict[int, str],
) -> Composition:
    """Calculate atomic fractions of each element in the simulation."""

    types, counts = np.unique(lmp.gather_atoms("type"), return_counts=True)
    species_count: dict[str, int] = {}

    for t, cnt in zip(types, counts):
        symbol = atom_type_symbols[t]
        species_count[symbol] = species_count.get(symbol, 0) + int(cnt)

    return Composition(species_count)


# === setting functions ===


def set_lammps_prism(
    lmp: LammpsLibrary,
    prism: Prism,
) -> None:
    """
    Set the LAMMPS simulation box using a Prism object.

    Parameters:
    ----------
    lmp
        A pylammpsmpi LAMMPS instance.
    prism
        An ASE Prism object defining the simulation box.
    """

    xhi, yhi, zhi, xy, xz, yz = prism.get_lammps_prism()

    region_type = "prism" if prism.is_skewed() else "block"

    coords: list[float] = [0.0, xhi, 0.0, yhi, 0.0, zhi]

    if region_type == "prism":
        coords += [xy, xz, yz]

    coords_str = " ".join(f"{c:.6f}" for c in coords)
    lmp.command(f"region 1 {region_type} {coords_str} units box")


def set_lammps_masses(
    lmp: LammpsLibrary,
    atom_types: dict[int, str],
) -> None:
    """Set the masses of atom types in LAMMPS.

    Parameters:
    ----------
    lmp
        A pylammpsmpi LAMMPS instance.
    atom_types
        A mapping of atom type IDs to element symbols.
    """

    for atom_type, symbol in atom_types.items():
        lmp.command(f"mass {atom_type} {atomic_masses[atomic_numbers[symbol]]}")


# === helper functions ===


def unique_pairs(iterable: Iterable[str]) -> list[tuple[str, str]]:
    """Generate unique pairs from an iterable of elements."""

    elems = sorted(set(iterable))
    return [
        (elems[i], elems[j])
        for i in range(len(elems))
        for j in range(i, len(elems))
    ]


def sort_atom_types(atom_types: dict[int, str]):
    """
    Group a mapping {type_id: element_symbol} into per-element groups,
    build LAMMPS-style asterisk (“range”) patterns, and prepare pair lists.

    Returns:
      * type_groups: {
          symbol: {
            "types": [int, …],      # the type IDs for this element
            "pattern": str          # e.g. "1*3" or "4"
          }
        }
      * elements:      tuple of symbols, sorted alphabetically
      * element_pairs: list of (sym1, sym2) for all unique pairs
      * pair_patterns: list of (pattern1, pattern2) matching element_pairs
    """

    type_groups: dict[str, dict[str, Any]] = {}
    for sym in sorted(set(atom_types.values())):
        type_groups[sym] = {"types": [], "pattern": ""}

    for t, sym in atom_types.items():
        type_groups[sym]["types"].append(t)

    for data in type_groups.values():
        ids = sorted(data["types"])
        if len(ids) > 1:
            data["pattern"] = f"{ids[0]}*{ids[-1]}"
        else:
            data["pattern"] = f"{ids[0]}"

    elements = tuple(sorted(type_groups.keys()))
    element_pairs = unique_pairs(list(elements))

    pair_patterns = [
        (type_groups[a]["pattern"], type_groups[b]["pattern"])
        for (a, b) in element_pairs
    ]

    return type_groups, elements, element_pairs, pair_patterns


def get_atom_types_from_ase(
    atoms: ase.Atoms,
) -> tuple[dict[int, str], list[int]]:
    """Extract atom types from an ASE Atoms object."""

    if not isinstance(atoms, ase.Atoms):
        raise TypeError("Expected an ASE Atoms object.")

    atom_types = {
        i: s for i, s in enumerate(sorted(atoms.symbols.indices().keys()), 1)
    }

    _atom_types_r = {v: k for k, v in atom_types.items()}
    all_types = [_atom_types_r[s] for s in atoms.get_chemical_symbols()]

    return atom_types, all_types
