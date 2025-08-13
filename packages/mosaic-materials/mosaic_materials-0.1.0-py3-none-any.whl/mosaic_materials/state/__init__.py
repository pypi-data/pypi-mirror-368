from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes

from mosaic_materials.misc.plot import set_style


@dataclass
class SimulationState:
    # --- property caches ---

    energy: float | None = None
    """ Total energy of the system. """

    rs: npt.NDArray[np.floating] | None = None
    rdf: dict[str, npt.NDArray[np.floating]] = field(default_factory=dict)
    """ Radial distribution function (RDF) data.

    `rs` is the radial distances, and `rdf` is the corresponding RDF values.
    The shape of `rdf` is (n_bins, n_pairs), where `n_bins` is the number of 
    radial bins and `n_pairs` is the number of element pairs in the system.

    These values will be used for total scattering calculations.
    """

    scattering_partials: dict[str, npt.NDArray[np.floating]] = field(
        default_factory=dict
    )
    """ Partial structure factor data for each element type pair."""

    scattering: dict[str, npt.NDArray[np.floating]] = field(
        default_factory=dict
    )
    """ Total structure factor data for each element type."""

    costs: dict[str, float] = field(default_factory=dict)
    """ Cost values for various constraints, indexed by constraint name. """

    def plot_scattering(
        self,
        name: str,
        x: npt.NDArray[np.floating] | None = None,
        y: npt.NDArray[np.floating] | None = None,
        show_diff: bool = True,
        ax: Axes | None = None,
        model_kwargs: Mapping[str, Any] | None = None,
        diff_kwargs: Mapping[str, Any] | None = None,
    ) -> Axes:
        """
        Plot experimental and model scattering for constraint `name`.

        Parameters
        ----------
        name
            The key under which this constraint stored its total scattering
            pattern in `self.scattering[name]`.
        exp_data
            Your `ScatteringData` object holding the experimental Q, F(Q), σ.
        ax
            Matplotlib Axes to draw on (defaults to `plt.gca()`).
        exp_kwargs
            Passed to `exp_data.plot(...)`.
        model_kwargs
            Passed to `ax.plot(...)` when drawing the model curve.

        Returns
        -------
        Axes
            The Axes you drew on.
        """

        set_style()

        _model_kwargs = dict(label="model", color="k", lw=1, zorder=2)
        _diff_kwargs = dict(
            label="difference",
            color="r",
            lw=0.75,
            zorder=0,
        )

        if ax is None:
            ax = plt.gca()

        if x is None:
            x = np.arange(0, self.scattering[name].size, dtype=np.float64)

        y_model = self.scattering[name]

        if model_kwargs:
            _model_kwargs.update(model_kwargs)

        if diff_kwargs:
            _diff_kwargs.update(diff_kwargs)

        ax.plot(x, y_model, **_model_kwargs)  # type: ignore[arg-type]

        # --- show difference ---
        if (y is not None) and show_diff:
            y_exp = y

            y_offset = min(
                y_exp.min(),
                y_model.min(),
            ) - 0.2 * abs(y_exp.max() - y_exp.min())

            ax.plot(
                x,
                y_model - y_exp + y_offset,
                **_diff_kwargs,  # type: ignore[arg-type]
            )

            ax.hlines(
                y_offset,
                x[0],
                x[-1],
                color="r",
                lw=0.5,
                ls="--",
                zorder=0,
            )

        return ax
