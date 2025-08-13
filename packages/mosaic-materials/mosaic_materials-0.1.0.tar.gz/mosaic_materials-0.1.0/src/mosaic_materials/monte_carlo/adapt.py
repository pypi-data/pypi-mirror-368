from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

import numpy as np

from mosaic_materials.moves.move import MoveStrategy
from mosaic_materials.state.system import System


@dataclass
class MoveSpec:
    """
    Generate a MC move and tune its proposal parameter (e.g. step size) to reach
    a target acceptance rate.
    """

    name: str
    move_class: type[MoveStrategy]
    selector: Callable[[System, np.random.Generator], Sequence[int]]
    kwargs: dict[str, Any]

    tuning_param: str | None = None
    target_acceptance: float = 0.5
    adjustment_factor: float = 1.1
    interval: int = 100

    # internal counters.
    _trial_count: int = field(default=0, init=False)
    _accept_count: int = field(default=0, init=False)

    def __post_init__(self):
        if self.tuning_param is None:
            self.tuning_param = getattr(self.move_class, "tuning_param", None)

    def instantiate(self, engine, rng: np.random.Generator) -> MoveStrategy:
        """Build one fresh MoveStrategy, drawing new atom_ids from selector."""

        atom_ids = self.selector(engine.system, rng)
        return self.move_class(
            engine,
            atom_ids=atom_ids,
            rng=rng,  # type: ignore[arg-type]
            **self.kwargs,
        )

    def record(self, accepted: bool) -> None:
        """
        Record one attempt outcome, and every `interval` trials adjust
        the `tuning_param` up or down to push acceptance toward target.
        """

        self._trial_count += 1
        if accepted:
            self._accept_count += 1

        if self._trial_count >= self.interval:
            observed = self._accept_count / self._trial_count
            if self.tuning_param is not None:
                old = self.kwargs[self.tuning_param]
                if observed > self.target_acceptance:
                    new = old * self.adjustment_factor
                else:
                    new = old / self.adjustment_factor
                self.kwargs[self.tuning_param] = new

            self._trial_count = 0
            self._accept_count = 0
