from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Type, TypeVar

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes

from mosaic_materials.misc.plot import set_style

T = TypeVar("T", bound="ScatteringData")


@dataclass
class ScatteringData:
    """
    Stores experimental total-scattering data and associated weights.

    Attributes
    ----------
    data
        Nx2 array where first column is Q, second is intensity.
    sigmas
        Per-point weight(s). Scalar is broadcast to all points.
    multiply_q
        Whether to multiply the simulated quantity by Q (used in x-ray).
    ones
        Typically an array of ones with length matching number of points.
    """

    data: np.ndarray
    sigmas: np.ndarray | float
    multiply_q: bool = False

    _weight_array: np.ndarray = field(init=False, repr=False)
    single_weight: bool = field(init=False)

    def __post_init__(self):
        if self.data.ndim != 2 or self.data.shape[1] < 2:
            raise ValueError(
                "`data` must be an Nx2 array with x in col 0 and y in col 1."
            )
        num_points = self.data.shape[0]

        if isinstance(self.sigmas, (int, float)):
            self._weight_array = np.full(num_points, float(self.sigmas))
            self.single_weight = True
        else:
            arr = np.asarray(self.sigmas, dtype=float)
            if arr.shape != (num_points,):
                raise ValueError(
                    f"`weight` must be scalar or shape ({num_points},), "
                    f"got {arr.shape}."
                )
            self._weight_array = arr
            self.single_weight = False

    @property
    def x(self) -> np.ndarray:
        return self.data[:, 0]

    @property
    def y(self) -> np.ndarray:
        return self.data[:, 1]

    @property
    def weight_array(self) -> np.ndarray:
        return self._weight_array

    def rescale_weight(self, factor: float):
        """Scale the weights in-place."""

        self._weight_array *= factor
        if self.single_weight:
            self.single_weight = False

    @classmethod
    def from_file(
        cls: Type[T],
        path: str | Path,
        sigmas: float | npt.NDArray[np.floating] | None = None,
        multiply_q: bool = False,
        **loadtxt_kwargs,
    ) -> T:
        """
        Load scattering data from a whitespace-delimited file.

        Expects 2 or 3 columns: Q, intensity [, sigma].

        Parameters
        ----------
        path
            Path to the data file.
        weight
            If the file has no sigma column, broadcast this scalar (or 1D array)
            to all points.  If None and file has 3 columns, use column 3.
            Defaults to 1.0 if neither provided.
        multiply_q
            Whether simulated S(Q) should be multiplied by Q.
        loadtxt_kwargs
            Extra kwargs passed to np.loadtxt (e.g. `delimiter`, `comments`).
        """

        arr = np.loadtxt(path, **loadtxt_kwargs)
        if arr.ndim != 2 or arr.shape[1] not in (2, 3):
            raise ValueError(
                f"File {path!r} must have 2 or 3 columns; got shape {arr.shape}"
            )

        data = arr[:, :2]
        if arr.shape[1] == 3:
            sigs = arr[:, 2]
            if sigmas is not None:
                sigs = sigmas
        else:
            sigs = sigmas if sigmas is not None else 1.0

        if isinstance(sigs, (int, float)):
            sigs = np.full(data.shape[0], float(sigs))

        return cls(data=data, sigmas=sigs, multiply_q=multiply_q)

    def multiply_by_q(self) -> None:
        """
        Multiply intensities by Q if not already multiplied; sets multiply_q.
        """
        if not self.multiply_q:
            self.data[:, 1] *= self.x
            self.multiply_q = True

    def divide_by_q(self) -> None:
        """
        Divide intensities by Q if currently multiplied; clears multiply_q.
        """
        if self.multiply_q:
            self.data[:, 1] /= self.x
            self.multiply_q = False

    def scale_intensity(self, factor: float, and_sigmas: bool = True) -> None:
        """
        Scale intensities by a factor and adjust sigmas accordingly so χ²
        remains meaningful.
        """
        self.data[:, 1] *= factor
        if and_sigmas:
            self._weight_array /= factor

    def save(
        self, path: str | Path, include_sigmas: bool = False, fmt: str = "%.6e"
    ) -> None:
        """
        Save data (and optional sigmas) to a whitespace-delimited file.
        """
        out = self.data.copy()
        if include_sigmas:
            out = np.column_stack((out, self._weight_array))

        np.savetxt(path, out, fmt=fmt)

    def plot(
        self,
        ax: Axes | None = None,
        plot_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """
        Plot the scattering data on the given axes.

        Parameters
        ----------
        ax
            The axes to plot on. If None, uses the current axes.
        label
            Label for the line in the legend.
        color
            Color of the line.
        plot_kwargs
            Additional keyword arguments passed to `ax.plot`.

        Returns
        -------
        Line2D
            The plotted line object.
        """

        set_style()

        if ax is None:
            ax = plt.gca()

        if plot_kwargs is None:
            plot_kwargs = {}

        _defaults = {
            "label": r"experiment",
            "edgecolor": "k",
            "facecolor": "none",
            "lw": 0.1,
            "zorder": 1,
            "s": 2,
        }

        _defaults.update(plot_kwargs)

        ax.scatter(
            self.x,
            self.y,
            **_defaults,
        )

        ax.set_xlabel(r"$Q$ ($\rm \AA{}^{-1}$)")
        ax.set_ylabel(r"$QF(Q)$" if self.multiply_q else r"$F(Q)$")

    def restrict_x(
        self,
        xmin: float | None = None,
        xmax: float | None = None,
        *,
        inplace: bool = False,
        closed: str = "both",
    ) -> "ScatteringData":
        """
        Restrict the data to xmin <= x <= xmax (by default).

        Parameters
        ----------
        xmin, xmax
            Range limits. Either may be None (open-ended).
        inplace
            If True, modify object and return self; otherwise return new one.
        closed
            Which endpoints are included:
            - "both":   xmin <= x <= xmax
            - "left":   xmin <= x <  xmax
            - "right":  xmin <  x <= xmax
            - "neither":xmin <  x <  xmax
        """
        x = self.x
        mask = np.ones(x.shape[0], dtype=bool)

        if xmin is not None:
            if closed in ("both", "left"):
                mask &= x >= xmin
            else:
                mask &= x > xmin
        if xmax is not None:
            if closed in ("both", "right"):
                mask &= x <= xmax
            else:
                mask &= x < xmax

        if not np.any(mask):
            raise ValueError("No points remain after x-range restriction.")

        new_data = self.data[mask]
        if self.single_weight:
            sigmas = float(self._weight_array[0])
        else:
            sigmas = self._weight_array[mask]

        if inplace:
            self.data = new_data

            if isinstance(sigmas, float):
                self._weight_array = np.full(
                    new_data.shape[0], sigmas, dtype=float
                )
                self.single_weight = True
            else:
                self._weight_array = np.asarray(sigmas, dtype=float)
                self.single_weight = False
            return self

        return ScatteringData(
            data=new_data, sigmas=sigmas, multiply_q=self.multiply_q
        )

    def find_peaks(
        self,
        *,
        x_range: tuple[float, float] | None = None,
        smooth: str | None = "savgol",
        window: int = 11,
        polyorder: int = 3,
        baseline: str | None = "median",
        min_height: float | None = None,
        min_prominence: float | None = None,
        min_distance: float | None = None,
        width: float | None = None,
        snr_threshold: float | None = None,
    ) -> tuple[np.ndarray, dict]:
        """
        Robust peak finding with optional smoothing, baseline subtraction,
        SNR gating, and prominence/distance/width thresholds.

        Returns
        -------
        idx
            Indices into the (possibly cropped) data array.
        prop
            Properties including 'x', 'y', and (if SciPy present) 'prominences',
            'widths', etc.
        """

        x = self.x
        y = self.y

        # --- crop in x if requested ---
        if x_range is not None:
            xmin, xmax = x_range
            m = (x >= xmin) & (x <= xmax)
            if not np.any(m):
                raise ValueError("No points remain after x_range crop.")
            x = x[m]
            y = y[m]

        # --- smoothing ---
        y_s = y.copy()
        if smooth is not None and window > 1:
            if smooth == "savgol":
                try:
                    from scipy.signal import savgol_filter

                    # window must be odd and >= polyorder+2
                    if window % 2 == 0:
                        window += 1
                    window = max(window, polyorder + 2 + (polyorder % 2 == 0))
                    y_s = savgol_filter(
                        y,
                        window_length=window,
                        polyorder=polyorder,
                        mode="interp",
                    )
                except Exception:
                    k = max(3, window | 1)
                    y_s = np.convolve(y, np.ones(k) / k, mode="same")

            elif smooth == "moving":
                k = max(3, window | 1)
                y_s = np.convolve(y, np.ones(k) / k, mode="same")

        # --- baseline subtraction ---
        if baseline == "median":
            base = np.median(y_s)
            y_b = y_s - base
        elif baseline == "p10":
            base = np.percentile(y_s, 10.0)
            y_b = y_s - base
        else:
            y_b = y_s

        # --- noise estimate (MAD) & SNR threshold to height ---
        if snr_threshold is not None and min_height is None:
            mad = np.median(np.abs(y_b - np.median(y_b))) + 1e-12
            sigma = 1.4826 * mad
            min_height = snr_threshold * sigma  # type: ignore

        # --- convert x-based distances/widths to samples ---
        dx = float(np.median(np.diff(x))) if x.size > 1 else 1.0
        distance_pts = (
            int(np.ceil((min_distance or 0.0) / dx)) if min_distance else None
        )
        width_pts = (width / dx) if width is not None else None

        # --- SciPy path if available ---
        try:
            from scipy.signal import find_peaks, peak_widths

            peaks, props = find_peaks(
                y_b,
                height=min_height,
                prominence=min_prominence,
                distance=distance_pts,
                width=width_pts,
            )
            # convert widths to x-units if present
            if "widths" in props:
                w_res = peak_widths(
                    y_b,
                    peaks,
                    rel_height=0.5 if width is None else None,  # type: ignore
                )
                # w_res = (widths, h_eval, left_ips, right_ips)
                props["widths"] = w_res[0] * dx
            props["prominences"] = props.get("prominences", None)
        except Exception:
            # --- NumPy fallback: simple local maxima + filtering ---
            left = y_b[1:-1] > y_b[:-2]
            right = y_b[1:-1] >= y_b[2:]
            cand = np.where(left & right)[0] + 1

            if min_height is not None:
                cand = cand[y_b[cand] >= min_height]

            def side_min(i, direction):
                j = i
                last = y_b[i]
                while 0 < j < len(y_b) - 1:
                    j += direction
                    if y_b[j] > last:  # rising again → stop
                        break
                    last = y_b[j]
                return y_b[max(min(j, len(y_b) - 1), 0)]

            prominences = np.array(
                [y_b[i] - max(side_min(i, -1), side_min(i, +1)) for i in cand]
            )
            if min_prominence is not None:
                keep = prominences >= min_prominence
                cand = cand[keep]
                prominences = prominences[keep]

            # enforce min_distance by greedy selection on descending height
            if distance_pts and cand.size:
                order = np.argsort(y_b[cand])[::-1]
                taken = []
                for idx in order:
                    p = cand[idx]
                    if all(abs(p - t) >= distance_pts for t in taken):
                        taken.append(p)
                cand = np.array(sorted(taken), dtype=int)

            peaks = cand
            props = {"prominences": prominences if cand.size else np.array([])}

        # common outputs
        props["x"] = x[peaks]
        props["y"] = y[peaks]
        props["y_proc"] = y_b[peaks]

        return peaks, props
