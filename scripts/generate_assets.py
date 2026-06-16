#!/usr/bin/env python3
"""Generate P5-style SVG assets for the fcitx5 skin.

All coordinates and colors are parameterized so the theme can be tuned
without hand-editing SVG files.
"""

from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class Palette:
    black: str = "#000000"
    panel: str = "#000000"
    crimson: str = "#E5191C"
    dark_red: str = "#A31417"
    bright_red: str = "#FF2A2A"
    white: str = "#ffffff"
    yellow: str = "#f2e852"


PALETTE = Palette()


def jagged_path(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    teeth: int,
    amplitude: float,
    seed: int | None = None,
    irregular: float = 0.55,
) -> str:
    """Return an SVG path data string for a torn, irregular saw-tooth edge.

    The ``amplitude`` sign controls the direction of the teeth.  A ``seed``
    makes the irregular height variation deterministic.  ``irregular`` (0..1)
    controls how much the tooth height varies from the base amplitude.
    """
    dx = x2 - x1
    dy = y2 - y1
    length = (dx * dx + dy * dy) ** 0.5
    if length == 0 or teeth <= 0:
        return f"M {x1:.2f} {y1:.2f}"

    ux = dx / length
    uy = dy / length
    # Unit vector perpendicular to the line (rotated 90 degrees CCW).
    px = -uy
    py = ux

    rng = random.Random(seed)
    commands: list[str] = [f"M {x1:.2f} {y1:.2f}"]
    for i in range(teeth):
        t_peak = (i + 0.5) / teeth
        t_end = (i + 1) / teeth
        sign = 1 if i % 2 == 0 else -1
        # Vary the height of each tooth for the hand-cut paper look.
        variation = 1.0 - irregular * rng.random()
        mag = amplitude * variation
        mx = x1 + ux * length * t_peak + px * sign * mag
        my = y1 + uy * length * t_peak + py * sign * mag
        ex = x1 + ux * length * t_end
        ey = y1 + uy * length * t_end
        commands.append(f"L {mx:.2f} {my:.2f} L {ex:.2f} {ey:.2f}")
    return " ".join(commands)


def _path_without_move(path: str) -> str:
    """Return an SVG path string with its initial ``M x y`` removed.

    Useful when continuing an existing sub-path with a jagged edge that was
    generated from right-to-left.  The first line-to command after the move
    becomes the first command of the continued path.
    """
    parts = path.split(None, 3)
    return parts[3] if len(parts) >= 4 else path


def star_path(
    cx: float,
    cy: float,
    outer: float,
    inner: float,
    points: int = 5,
    rotation: float = -90.0,
) -> str:
    """Return an SVG path data string for a regular star polygon."""
    commands: list[str] = []
    start = math.radians(rotation)
    step = math.pi / points
    for i in range(points * 2):
        angle = start + i * step
        radius = outer if i % 2 == 0 else inner
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        commands.append(f"{x:.2f},{y:.2f}")
    return f"M {commands[0]} L " + " L ".join(commands[1:]) + " Z"


def chamfered_rect_path(x: float, y: float, w: float, h: float, chamfer: float) -> str:
    """Return an SVG path for a rectangle with cut (chamfered) corners."""
    c = min(chamfer, w / 2, h / 2)
    return (
        f"M {x + c} {y} L {x + w - c} {y} L {x + w} {y + c} "
        f"L {x + w} {y + h - c} L {x + w - c} {y + h} "
        f"L {x + c} {y + h} L {x} {y + h - c} L {x} {y + c} Z"
    )


def svg_root(width: int, height: int, content: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}">\n'
        f"{content}\n"
        f"</svg>"
    )


def button_svg_content(
    x: float,
    y: float,
    w: float,
    h: float,
    chamfer: float,
    shadow_dx: float,
    shadow_dy: float,
    fill: str,
    border: str,
    shadow: str,
    border_width: float,
    inset_width: float,
) -> str:
    """Build a P5-style chamfered button: red drop-shadow + thick white border."""
    shadow_path = chamfered_rect_path(x + shadow_dx, y + shadow_dy, w, h, chamfer)
    body_path = chamfered_rect_path(x, y, w, h, chamfer)
    inset = min(inset_width, chamfer - 1)
    inner_path = chamfered_rect_path(
        x + inset, y + inset, w - inset * 2, h - inset * 2, chamfer - inset
    )
    return (
        f'  <path d="{shadow_path}" fill="{shadow}"/>\n'
        f'  <path d="{body_path}" fill="{fill}" stroke="{border}" '
        f'stroke-width="{border_width}" stroke-linejoin="round"/>\n'
        f'  <path d="{inner_path}" fill="none" stroke="{border}" '
        f'stroke-width="1" opacity="0.9"/>\n'
    )


def generate_panel(
    width: int = 260,
    height: int = 56,
    point: float = 16.0,
    left_slant: float = 6.0,
    stroke_width: float = 4.5,
) -> str:
    """Input panel background: a black tag with blunt right arrow and white outline."""
    p = PALETTE
    notch = min(point, height * 0.32)
    s = stroke_width / 2

    # Tag shape: left side slightly slanted, right side a blunt arrow point.
    # Bottom-left is inset so the left edge slopes the same way as the
    # reference image in 结果.jpg.
    body_d = (
        f"M {s} {s} "
        f"L {width - notch - s} {s} "
        f"L {width - s} {height / 2} "
        f"L {width - notch - s} {height - s} "
        f"L {left_slant + s} {height - s} Z"
    )

    content = (
        f'  <path d="{body_d}" fill="{p.black}" stroke="{p.white}" '
        f'stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
    )
    return svg_root(width, height, content)


def generate_highlight(
    width: int = 160,
    height: int = 36,
    pad: int = 2,
) -> str:
    """Candidate highlight: a flat red rectangle behind the selected candidate."""
    p = PALETTE
    content = (
        f'  <rect x="{pad}" y="{pad}" width="{width - pad * 2}" '
        f'height="{height - pad * 2}" fill="{p.crimson}"/>\n'
    )
    return svg_root(width, height, content)


def generate_menu_panel(
    width: int = 220,
    height: int = 48,
    point: float = 14.0,
    left_slant: float = 5.0,
    stroke_width: float = 4.0,
) -> str:
    """Right-click menu background: smaller black tag with blunt right arrow."""
    p = PALETTE
    notch = min(point, height * 0.32)
    s = stroke_width / 2

    body_d = (
        f"M {s} {s} "
        f"L {width - notch - s} {s} "
        f"L {width - s} {height / 2} "
        f"L {width - notch - s} {height - s} "
        f"L {left_slant + s} {height - s} Z"
    )

    content = (
        f'  <path d="{body_d}" fill="{p.black}" stroke="{p.white}" '
        f'stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
    )
    return svg_root(width, height, content)


def generate_menu_highlight(
    width: int = 160,
    height: int = 28,
    pad: int = 2,
) -> str:
    """Menu item highlight: a flat red rectangle behind the selected menu item."""
    p = PALETTE
    content = (
        f'  <rect x="{pad}" y="{pad}" width="{width - pad * 2}" '
        f'height="{height - pad * 2}" fill="{p.crimson}"/>\n'
    )
    return svg_root(width, height, content)


def generate_arrow(size: int = 16) -> str:
    """Submenu arrow / page button: a simple white right-pointing triangle."""
    p = PALETTE
    path_d = f"M 0,0 L {size},{size / 2} L 0,{size} Z"
    content = f'  <path d="{path_d}" fill="{p.white}"/>\n'
    return svg_root(size, size, content)


def generate_checkbox(size: int = 16) -> str:
    """Menu checkbox: a chamfered black box with white border and white check."""
    p = PALETTE
    pad = 2
    box_size = size - pad * 2
    chamfer = 2.0
    box_d = chamfered_rect_path(pad, pad, box_size, box_size, chamfer)

    content = (
        f'  <path d="{box_d}" fill="{p.black}" stroke="{p.white}" '
        f'stroke-width="2" stroke-linejoin="round"/>\n'
        f'  <polyline points="4,{size / 2 + 1} {size / 2 - 1},{size - 4} {size - 3},{4}" '
        f'fill="none" stroke="{p.white}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round"/>\n'
    )
    return svg_root(size, size, content)


def write_asset(directory: Path, name: str, svg: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(svg, encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate P5-style fcitx5 skin assets."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dist" / "p5-phantom-skin",
        help="Output directory for generated assets.",
    )
    args = parser.parse_args(argv)

    out = args.out
    write_asset(out, "panel.svg", generate_panel())
    write_asset(out, "highlight.svg", generate_highlight())
    write_asset(out, "menu-panel.svg", generate_menu_panel())
    write_asset(out, "menu-highlight.svg", generate_menu_highlight())
    write_asset(out, "arrow.svg", generate_arrow())
    write_asset(out, "checkbox.svg", generate_checkbox())

    print(f"Generated assets in: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
