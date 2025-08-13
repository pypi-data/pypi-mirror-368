from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Sequence

import h5py
import numpy as np

from mosaic_materials.monte_carlo.adapt import MoveSpec
from mosaic_materials.state.system import get_lammps_cell


class MCTrajectory:
    """
    HDF5 trajectory writer for Monte Carlo runs.

    Features
    --------
    - Append new frames every `every` steps via `maybe_write(...)`
    - Creates extendable, compressed datasets (positions, meta)
    - Safe append to an existing file (validates atom count & schema)
    - Optional box tracking (auto-on if any move changes the box)
    - Optional file rollover when size exceeds `max_bytes`
    """

    def __init__(
        self,
        path: str | Path,
        engine,
        *,
        move_specs: Sequence[MoveSpec] | None = None,
        every: int = 100,
        include_cell: bool | None = None,
        store_images: bool = False,
        compression: str | None = "gzip",
        compression_opts: int | None = 4,
        pos_dtype=np.float32,
        append: bool = False,
        max_bytes: int | None = None,
    ):
        self.path_base = Path(path)
        self.engine = engine
        self.system = engine.system
        self.every = int(every)
        self.store_images = bool(store_images)
        self.compression = compression
        self.compression_opts = compression_opts
        self.pos_dtype = pos_dtype
        self.append = append
        self.max_bytes = max_bytes
        self.file_idx = 0
        self._h5: h5py.File | None = None
        self._frames = None
        self._static = None
        self._n_atoms = int(self.system.all_atom_ids.size)

        # Decide whether to store the box
        if include_cell is None:
            include_cell = False
            if move_specs:
                # Convention: move_class sets class attr `changes_box = True`
                include_cell = any(
                    getattr(spec.move_class, "changes_box", False)
                    for spec in move_specs
                )
        self.include_cell = include_cell

        # Build a filename scheme if user didn't include an index placeholder.
        # If `path` already exists and append=False, it will be overwritten.
        self._open_file(self._indexed_path(self.file_idx), append=self.append)

    # --------------------------- public API ---------------------------

    def maybe_write(
        self,
        step: int,
        *,
        temperature: float | None,
        pressure: float | None,
        chi2: float,
        U: float,
        V: float,
        accepted: bool,
    ) -> None:
        """Write a frame if `step % every == 0`."""

        if step % self.every != 0:
            return

        self.write_frame(step, temperature, pressure, chi2, U, V, accepted)

    def write_frame(
        self,
        step: int,
        temperature: float | None,
        pressure: float | None,
        chi2: float,
        U: float,
        V: float,
        accepted: bool,
    ) -> None:
        """Append one snapshot to the trajectory."""

        assert self._h5 is not None

        # Gather structure (wrapped positions in Å; optional image flags)
        x_wrapped = self.engine.lmp.gather_atoms("x")
        pos = self.system.prism.vector_to_ase(x_wrapped).astype(self.pos_dtype)

        imgs = None
        if self.store_images:
            imgs = self.engine.lmp.gather_atoms("image").astype(np.int32)

        cell = None
        if self.include_cell:
            cell = get_lammps_cell(self.engine.lmp, self.engine.units).astype(
                np.float64
            )  # (3,3)

        t = float(time.time())
        accepted_u8 = np.uint8(1 if accepted else 0)

        assert self._frames is not None, "Frames group not initialised."

        # Extend datasets by 1
        idx = self._frames["step"].shape[0]
        self._frames["step"].resize(idx + 1, axis=0)
        self._frames["time"].resize(idx + 1, axis=0)
        self._frames["temperature"].resize(idx + 1, axis=0)
        self._frames["pressure"].resize(idx + 1, axis=0)
        self._frames["chi2"].resize(idx + 1, axis=0)
        self._frames["U"].resize(idx + 1, axis=0)
        self._frames["V"].resize(idx + 1, axis=0)
        self._frames["accepted"].resize(idx + 1, axis=0)
        self._frames["positions"].resize((idx + 1, self._n_atoms, 3))
        if self.include_cell:
            self._frames["cell"].resize((idx + 1, 3, 3))
        if self.store_images:
            self._frames["images"].resize((idx + 1, self._n_atoms, 3))

        # Write
        self._frames["step"][idx] = step
        self._frames["time"][idx] = t
        self._frames["temperature"][idx] = (
            np.nan if temperature is None else float(temperature)
        )
        self._frames["pressure"][idx] = (
            np.nan if pressure is None else float(pressure)
        )
        self._frames["chi2"][idx] = float(chi2)
        self._frames["U"][idx] = float(U)
        self._frames["V"][idx] = float(V)
        self._frames["accepted"][idx] = accepted_u8
        self._frames["positions"][idx, :, :] = pos
        if self.include_cell:
            self._frames["cell"][idx, :, :] = cell
        if self.store_images and imgs is not None:
            self._frames["images"][idx, :, :] = imgs

        self._h5.flush()

        if self.max_bytes is not None:
            self._rollover_if_needed()

    def close(self) -> None:
        if self._h5 is not None:
            self._h5.flush()
            self._h5.close()
            self._h5 = None

    def __enter__(self) -> "MCTrajectory":
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # ------------------------ internal helpers ------------------------

    def _indexed_path(self, idx: int) -> Path:
        """Return path with an integer suffix if base has no placeholder."""

        p = self.path_base
        if "{" in str(p) and "}" in str(p):
            # user provided a template like "traj_{:03d}.h5"
            return Path(str(p).format(idx))
        if idx == 0:
            return p
        stem = p.stem
        return p.with_stem(f"{stem}_{idx:03d}")

    def _open_file(self, path: Path, append: bool) -> None:
        exists = path.exists()
        mode = "a" if (exists and append) else "w"
        self._h5 = h5py.File(path, mode, libver="latest")
        self._ensure_layout(append=exists and append)

    def _ensure_layout(self, append: bool) -> None:
        """Create or validate the file layout."""

        assert self._h5 is not None
        h5 = self._h5

        if not append:
            # fresh file: write static info and create extendable datasets
            # -- static group
            g_static = h5.require_group("static")
            self._static = g_static

            # Atom metadata
            atom_ids = self.system.all_atom_ids.astype(np.int32)
            types = self.engine.lmp.gather_atoms("type").astype(np.int16)
            g_static.create_dataset("atom_ids", data=atom_ids, dtype=np.int32)
            g_static.create_dataset("type_ids", data=types, dtype=np.int16)

            # Optional molecule IDs (if present)
            try:
                mol_ids = self.engine.lmp.gather_atoms("molecule").astype(
                    np.int32
                )
                g_static.create_dataset(
                    "molecule_ids", data=mol_ids, dtype=np.int32
                )
            except Exception:
                pass

            # Type mapping (store as JSON attr)
            # e.g., {"1":"C","2":"H","3":"Zn"}
            type_map = self.system.atom_types
            g_static.attrs["type_map_json"] = json.dumps(type_map)

            # File attrs
            h5.attrs["created_unix"] = float(time.time())
            h5.attrs["units_style"] = str(self.engine.units)
            h5.attrs["include_cell"] = bool(self.include_cell)
            h5.attrs["store_images"] = bool(self.store_images)
            h5.attrs["pos_dtype"] = np.dtype(self.pos_dtype).name
            h5.attrs["writer"] = "MCTrajectory v1"

            # -- frames group
            g = h5.require_group("frames")
            self._frames = {
                "step": g.create_dataset(
                    "step", shape=(0,), maxshape=(None,), dtype=np.int64
                ),
                "time": g.create_dataset(
                    "time", shape=(0,), maxshape=(None,), dtype=np.float64
                ),
                "temperature": g.create_dataset(
                    "temperature",
                    shape=(0,),
                    maxshape=(None,),
                    dtype=np.float32,
                ),
                "pressure": g.create_dataset(
                    "pressure", shape=(0,), maxshape=(None,), dtype=np.float32
                ),
                "chi2": g.create_dataset(
                    "chi2",
                    shape=(0,),
                    maxshape=(None,),
                    dtype=np.float64,
                    compression=self.compression,
                    compression_opts=self.compression_opts,
                    chunks=True,
                ),
                "U": g.create_dataset(
                    "U",
                    shape=(0,),
                    maxshape=(None,),
                    dtype=np.float64,
                    compression=self.compression,
                    compression_opts=self.compression_opts,
                    chunks=True,
                ),
                "V": g.create_dataset(
                    "V",
                    shape=(0,),
                    maxshape=(None,),
                    dtype=np.float64,
                    compression=self.compression,
                    compression_opts=self.compression_opts,
                    chunks=True,
                ),
                "accepted": g.create_dataset(
                    "accepted",
                    shape=(0,),
                    maxshape=(None,),
                    dtype=np.uint8,
                ),
                "positions": g.create_dataset(
                    "positions",
                    shape=(0, self._n_atoms, 3),
                    maxshape=(None, self._n_atoms, 3),
                    dtype=self.pos_dtype,
                    compression=self.compression,
                    compression_opts=self.compression_opts,
                    chunks=(1, min(self._n_atoms, 8192), 3),
                ),
            }
            if self.include_cell:
                self._frames["cell"] = g.create_dataset(
                    "cell",
                    shape=(0, 3, 3),
                    maxshape=(None, 3, 3),
                    dtype=np.float64,
                    compression=self.compression,
                    compression_opts=self.compression_opts,
                    chunks=True,
                )
            if self.store_images:
                self._frames["images"] = g.create_dataset(
                    "images",
                    shape=(0, self._n_atoms, 3),
                    maxshape=(None, self._n_atoms, 3),
                    dtype=np.int32,
                    compression=self.compression,
                    compression_opts=self.compression_opts,
                    chunks=(1, min(self._n_atoms, 8192), 3),
                )

        else:
            # append: validate layout and pick up handles
            g_static = h5["static"]
            self._static = g_static
            g = h5["frames"]
            self._frames = {name: g[name] for name in g}

            # Check atom count compatibility
            n_file = int(g_static["atom_ids"].shape[0])
            if n_file != self._n_atoms:
                raise ValueError(
                    f"Cannot append: file has {n_file} atoms, current system "
                    f"has {self._n_atoms}."
                )

            # Check include_cell / store_images compatibility
            if bool(h5.attrs.get("include_cell", False)) != bool(
                self.include_cell
            ):
                raise ValueError(
                    "Cannot append: include_cell mismatch between file and "
                    "current settings."
                )
            if bool(h5.attrs.get("store_images", False)) != bool(
                self.store_images
            ):
                raise ValueError(
                    "Cannot append: store_images mismatch between file and "
                    "current settings."
                )

    def _rollover_if_needed(self) -> None:
        """If file exceeds `max_bytes`, close it and open the next index."""

        if self._h5 is None or self.max_bytes is None:
            return
        # ensure all data is on disk
        self._h5.flush()
        p = Path(self._h5.filename)  # type: ignore[attr-defined]
        try:
            size = p.stat().st_size
        except FileNotFoundError:
            return
        if size <= self.max_bytes:
            return
        # roll
        self.close()
        self.file_idx += 1
        self._open_file(self._indexed_path(self.file_idx), append=False)


def make_hdf5_writer(
    traj: MCTrajectory,
    *,
    only_on_accept: bool = False,
) -> "DriverCallback":
    """
    Turn an `MCTrajectory` into an MCDriver callback.

    Parameters
    ----------
    only_on_accept
        If True, only write a frame for accepted steps (and still respect
        `traj.every`).
    """

    def _cb(driver, step, spec, accepted, chi2, U, V):
        if only_on_accept and not accepted:
            return
        traj.maybe_write(
            step,
            temperature=driver.temperature,
            pressure=driver.pressure,
            chi2=chi2,
            U=U,
            V=V,
            accepted=accepted,
        )

    return _cb
