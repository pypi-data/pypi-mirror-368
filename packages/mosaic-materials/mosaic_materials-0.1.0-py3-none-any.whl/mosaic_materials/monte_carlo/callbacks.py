from __future__ import annotations

import csv
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Sequence

from mosaic_materials.monte_carlo.adapt import MoveSpec

if TYPE_CHECKING:
    from mosaic_materials.monte_carlo.driver import MCDriver

DriverCallback = Callable[
    [
        "MCDriver",  # main driver
        int,  # step
        MoveSpec,  # which move‐spec was used
        bool,  # accepted?
        float,  # χ²
        float,  # U
        float,  # V
    ],
    None,
]


def summary_logger(
    path: str | Path,
    *,
    interval: int = 100,
    include_constraints: bool = True,
    include_temperature: bool = True,
    include_beta: bool = False,
    include_pressure: bool = True,
):
    """
    Append one row every `interval` steps with:

      - step
      - timestamp (local ISO8601)
      - [temperature_K], [beta], [pressure]
      - total_accepted, total_rejected
      - [per-constraint costs]
      - avg_time_per_step
    """
    path = Path(path)
    start_perf = time.perf_counter()
    total_accept = 0
    total_reject = 0

    header_written = False
    fieldnames: list[str] = []

    def _logger(driver, step, spec, accepted, chi2, U, V):
        nonlocal total_accept, total_reject, header_written, fieldnames

        if accepted:
            total_accept += 1
        else:
            total_reject += 1

        if step % interval != 0:
            return

        now_iso = datetime.now().astimezone().isoformat()
        elapsed = time.perf_counter() - start_perf

        if not header_written:
            fieldnames = ["step", "timestamp"]
            if include_temperature:
                fieldnames.append("temperature_K")
            if include_beta:
                fieldnames.append("beta")
            if include_pressure:
                fieldnames.append("pressure")

            fieldnames += [
                "total_accepted",
                "total_rejected",
                "avg_time_per_step",
            ]
            if include_constraints:
                # fixed order so downstream parsing is stable
                fieldnames.extend(sorted(driver.state.costs.keys()))

            with open(path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

            header_written = True

        row = {
            "step": step,
            "timestamp": now_iso,
            "total_accepted": total_accept,
            "total_rejected": total_reject,
            "avg_time_per_step": elapsed / step,
        }

        if include_temperature:
            row["temperature_K"] = float(driver.temperature)
        if include_beta:
            row["beta"] = float(driver.beta)
        if include_pressure:
            row["pressure"] = (
                "" if driver.pressure is None else float(driver.pressure)
            )

        if include_constraints:
            for name in fieldnames:
                if name in driver.state.costs:
                    row[name] = driver.state.costs[name]

        with open(path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(row)

    return _logger


def move_magnitude_tuning_logger(
    move_specs: Sequence[MoveSpec],
    logger: logging.Logger | None = None,
) -> Callable[..., None]:
    """A callback that logs tuning parameter changes for each MoveSpec."""

    logger = logger or logging.getLogger(__name__)

    last_values = {
        spec.name: spec.kwargs.get(spec.tuning_param)
        if spec.tuning_param is not None
        else None
        for spec in move_specs
    }

    def tuning_logger(
        driver,
        step: int,
        spec: MoveSpec,
        accepted: bool,
        chi2: float,
        U: float,
        V: float,
    ):
        tp = spec.tuning_param
        if tp is None:
            return
        prev = last_values[spec.name]
        current = spec.kwargs[tp]
        if prev is None or current == prev:
            return

        arrow = "↑" if current > prev else "↓"

        logger.info(
            f"[step {step:5d}] {spec.name}.{tp}: "
            f"{prev:.4g} {arrow} {current:.4g}"
        )
        last_values[spec.name] = current

    return tuning_logger
