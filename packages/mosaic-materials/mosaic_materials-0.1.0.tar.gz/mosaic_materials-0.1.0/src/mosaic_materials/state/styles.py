import difflib
import shutil
import textwrap
from typing import Final, Iterable, Literal, Tuple, Union, get_args

UnitStyle = Literal[
    "lj", "real", "metal", "si", "cgs", "electron", "micro", "nano"
]

BoundaryStyle = Literal["p", "f", "s", "m"]
Boundary = Tuple[BoundaryStyle, BoundaryStyle, BoundaryStyle]
BoundaryInput = Union[BoundaryStyle, str, Tuple[str, ...], Iterable[str]]

AtomStyle = Literal[
    "amoeba",
    "angle",
    "apip",
    "atomic",
    "body",
    "bond",
    "bpm/sphere",
    "charge",
    "dielectric",
    "dipole",
    "dpd",
    "edpd",
    "electron",
    "ellipsoid",
    "full",
    "hybrid",
    "line",
    "mdpd",
    "molecular",
    "oxdna",
    "peri",
    "smd",
    "sph",
    "sphere",
    "spin",
    "template",
    "tri",
    "wavepacket",
]

DEFAULT_UNITS: Final[UnitStyle] = "metal"
DEFAULT_BOUNDARY: Final[Boundary] = ("p", "p", "p")
DEFAULT_ATOM_STYLE: Final[AtomStyle] = "full"

_ALLOWED_UNIT_STYLES: set[str] = set(get_args(UnitStyle))
_ALLOWED_BOUNDARY_STYLES: set[str] = set(get_args(BoundaryStyle))
_ALLOWED_ATOM_STYLES: set[str] = set(get_args(AtomStyle))


def _suggest_closest(value: str, choices: Iterable[str]) -> str | None:
    matches = difflib.get_close_matches(value, list(choices), n=1, cutoff=0.6)
    return matches[0] if matches else None


def _format_choices(
    choices: Iterable[str], max_width: int | None = None
) -> str:
    """
    Nicely format a list of choices into wrapped columns.
    """

    choices = sorted(choices)
    if max_width is None:
        try:
            max_width = shutil.get_terminal_size().columns
        except Exception:
            max_width = 80

    joined = "  ".join(choices)
    return textwrap.indent(textwrap.fill(joined, width=max_width), "    ")


def validate_unit_style(u: str) -> UnitStyle:
    if u not in _ALLOWED_UNIT_STYLES:
        suggestion = _suggest_closest(u, _ALLOWED_UNIT_STYLES)
        formatted = _format_choices(_ALLOWED_UNIT_STYLES)
        msg_lines = [
            f"Invalid unit style: {u!r}.",
            "Allowed values are:",
            formatted,
        ]
        if suggestion:
            msg_lines.append(f"Did you mean {suggestion!r}?")
        raise ValueError("\n".join(msg_lines))
    return u  # type: ignore[return-value]


def validate_atom_style(style: str) -> AtomStyle:
    if style not in _ALLOWED_ATOM_STYLES:
        suggestion = _suggest_closest(style, _ALLOWED_ATOM_STYLES)
        formatted = _format_choices(_ALLOWED_ATOM_STYLES)
        msg_lines = [
            f"Invalid atom_style: {style!r}.",
            "Allowed values are:",
            formatted,
        ]
        if suggestion:
            msg_lines.append(f"Did you mean {suggestion!r}?")
        raise ValueError("\n".join(msg_lines))
    return style  # type: ignore[return-value]


def normalise_boundary(b: BoundaryInput) -> Boundary:
    """
    Normalise various boundary specifications to a 3-tuple of BoundaryStyle.

    Accepts:
      * Single style: "p" or 'f' -> ("p","p","p")
      * Space-separated string: "p f s" -> ("p","f","s")
      * Iterable length 3: ("p","f","s") or ["p","f","s"]
    """
    allowed = {"p", "f", "s", "m"}

    if isinstance(b, str):
        parts = b.strip().split()
        if len(parts) == 1:
            parts = parts * 3
        elif len(parts) != 3:
            raise ValueError(
                f"Boundary string must have 1 or 3 entries, got: {b!r}"
            )
    elif isinstance(b, (tuple, list)):
        if len(b) == 1:
            parts = [b[0]] * 3  # type: ignore
        elif len(b) == 3:
            parts = list(b)  # type: ignore
        else:
            raise ValueError(
                f"Boundary iterable must have length 1 or 3, got: {b!r}"
            )
    else:
        raise TypeError(f"Unsupported boundary type: {type(b)}")

    normalised: list[BoundaryStyle] = []
    for i, p in enumerate(parts):
        if p not in allowed:
            raise ValueError(
                f"Invalid boundary style '{p}' at position {i}; allowed: "
                "{sorted(allowed)}"
            )
        normalised.append(p)  # type: ignore

    return (normalised[0], normalised[1], normalised[2])  # type: ignore


def boundary_str(boundary: Boundary) -> str:
    return " ".join(boundary)
