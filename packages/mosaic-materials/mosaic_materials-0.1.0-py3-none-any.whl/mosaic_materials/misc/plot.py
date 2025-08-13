from typing import Any, Mapping

import matplotlib.pyplot as plt

_cm_to_inch: float = 1 / 2.54

STYLE_DEFAULTS: Mapping[str, Any] = {
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "axes.spines.top": True,
    "axes.spines.right": True,
    "font.family": "Helvetica",
    "font.size": 7,
    "figure.figsize": (4 * _cm_to_inch, 3 * _cm_to_inch),
    "legend.fancybox": False,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.frameon": False,
    "xtick.direction": "in",
    "xtick.top": True,
    "ytick.direction": "in",
    "ytick.right": True,
    "savefig.transparent": True,
    "savefig.bbox": "tight",
    "figure.dpi": 300,
}


def set_style() -> None:
    """Update matplotlib's rcParams with STYLE_DEFAULTS."""

    plt.rcParams.update(STYLE_DEFAULTS)
