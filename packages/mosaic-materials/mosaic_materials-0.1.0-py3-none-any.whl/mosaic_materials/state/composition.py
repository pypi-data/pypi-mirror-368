from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import cached_property, reduce
from math import gcd
from typing import Iterable, Mapping

import numpy as np


@dataclass(frozen=True)
class Composition:
    """
    Lightweight composition similar in spirit to pymatgen's, but minimal.
    Stores species counts (must be nonnegative).
    """

    species_counts: Mapping[str, int]

    def __post_init__(self):
        clean: dict[str, int] = {}
        for el, cnt in self.species_counts.items():
            if not isinstance(cnt, (int, np.integer)):
                raise TypeError(
                    f"Count for element '{el}' must be integer, got {type(cnt)}"
                )
            if cnt < 0:
                raise ValueError(
                    f"Count for element '{el}' must be non-negative, got {cnt}"
                )
            if cnt == 0:
                continue
            clean[el] = int(cnt)

        if not clean:
            raise ValueError(
                "Composition must have at least one element with positive count"
            )

        object.__setattr__(self, "species_counts", dict(sorted(clean.items())))

    @cached_property
    def natoms(self) -> int:
        """Total number of atoms (sum of counts)."""

        return sum(self.species_counts.values())

    @cached_property
    def elements(self) -> list[str]:
        """Sorted list of unique elements."""

        return list(self.species_counts.keys())

    @cached_property
    def fractional_composition(self) -> dict[str, float]:
        """Atomic fraction per element."""

        total = self.natoms
        return {el: cnt / total for el, cnt in self.species_counts.items()}

    def atomic_fraction(self, el: str) -> float:
        """Atomic fraction of a given element."""

        if el not in self.species_counts:
            raise KeyError(f"Element '{el}' not in composition")

        return self.species_counts[el] / self.natoms

    @cached_property
    def reduced_formula_and_factor(self) -> tuple[str, int]:
        """Return (reduced_formula, factor) where factor is the divisor."""

        counts = list(self.species_counts.values())
        factor = _multi_gcd(counts)
        if factor <= 1:
            formula = self.formula
            return formula, 1

        reduced_parts = []
        for el, cnt in self.species_counts.items():
            reduced_cnt = cnt // factor
            reduced_parts.append(f"{el}{reduced_cnt}")
        formula = " ".join(reduced_parts)
        return formula, factor

    @cached_property
    def formula(self) -> str:
        """Unreduced formula, in the order of elements."""

        return " ".join(f"{el}{cnt}" for el, cnt in self.species_counts.items())

    def __add__(self, other: Composition) -> Composition:
        if not isinstance(other, Composition):
            return NotImplemented
        merged = Counter(self.species_counts) + Counter(other.species_counts)
        return Composition(dict(merged))

    def as_dict(self) -> dict[str, int]:
        """Raw species counts dict."""

        return dict(self.species_counts)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Composition):
            return False
        return self.species_counts == other.species_counts

    def __repr__(self) -> str:
        return f"Composition({self.formula})"

    def __str__(self) -> str:
        return self.formula


# === Helper functions ===


def _multi_gcd(values: Iterable[int]) -> int:
    """GCD of multiple integers."""

    return reduce(gcd, values)
