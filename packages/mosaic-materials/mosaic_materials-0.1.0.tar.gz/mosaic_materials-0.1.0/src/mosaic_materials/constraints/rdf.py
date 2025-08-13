from __future__ import annotations

from concurrent.futures import Future
from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt

from mosaic_materials.constraints.constraint import Constraint
from mosaic_materials.state import SimulationState

if TYPE_CHECKING:
    from mosaic_materials.engine import MCEngine


class RDFConstraint(Constraint):
    """A constraint that calculates the radial distribution function (RDF)."""

    def __init__(
        self,
        name: str = "c_rdf",
        r_max: float | None = None,
        bin_width: float = 0.02,
        weight: float = 1.0,
        cutoff_buffer: float = 1.0,
    ):
        super().__init__(weight=weight)
        self.name = name
        self.r_max = r_max
        self.bin_width = bin_width
        self.cutoff_buffer = cutoff_buffer

        self._r_values: npt.NDArray[np.floating] | None = None
        self._nbins: int | None = None
        self._arr_width: int | None = None
        self._compute_id: str | None = None

    def install(self, engine: MCEngine):
        super().install(engine)

        assert engine.system is not None, (
            "System must be set before installing RDFConstraint."
        )

        r_max = self.r_max or min(engine.system.cell_lengths) / 2
        n_bins = int(np.floor(r_max / self.bin_width)) + 1

        pair_str = " ".join(
            f"{a} {b}" for a, b in engine.system.element_pair_patterns
        )

        cid = self.name
        engine.register_compute(cid)

        engine.lmp.command("neighbor 1.0 bin")
        engine.lmp.command("neigh_modify delay 200 every 1 check yes")
        engine.lmp.command("neigh_modify one 100000 page 1000000")
        engine.lmp.command(f"comm_modify cutoff {r_max + self.cutoff_buffer}")
        engine.lmp.command(
            f"compute {cid} all rdf {n_bins} {pair_str} cutoff {r_max}"
        )
        engine.lmp.command("run 0")

        self._compute_id = cid
        self.r_max = r_max
        self._nbins = n_bins
        self._arr_width = len(engine.system.element_pair_patterns) * 2 + 1

        self._r_values = engine.lmp.extract_compute(
            self._compute_id, 0, 2, self._nbins, self._arr_width
        )[:, 0]

    def compute(self, state: SimulationState) -> float:
        """
        Extract the RDF from LAMMPS and cache it in state.rdf. For now we do not
        support turning the RDF into a cost, so this returns 0.0.
        """

        assert self.installed and self.engine is not None, (
            f"RDFConstraint `{self.name}` must be installed before computing."
        )

        if self.engine._needs_compute:
            self.engine.lmp.command("run 0")

        result = self.engine.lmp.extract_compute(
            self._compute_id, 0, 2, self._nbins, self._arr_width
        )

        raw = result.result() if isinstance(result, Future) else result

        rs = raw[:, 0]
        rdf = raw[:, 1::2].T
        key = self.label()

        state.rs = rs
        state.rdf = state.rdf or {}
        state.rdf[key] = rdf

        return 0.0

    def label(self) -> str:
        return self.name

    def teardown(self) -> None:
        """Remove the RDF compute from LAMMPS."""

        assert self.engine is not None, "Engine must be set before teardown."

        if self._compute_id:
            self.engine.lmp.command(f"uncompute {self._compute_id}")
            self.engine.unregister_compute(self._compute_id)
            self._compute_id = None
