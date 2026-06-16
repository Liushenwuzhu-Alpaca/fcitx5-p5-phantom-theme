#!/usr/bin/env python3
"""Generate P5-style SVG assets for the fcitx5 skin.

All coordinates and colors are parameterized so the theme can be tuned
without hand-editing SVG files.
"""

from __future__ import annotations

import argparse
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


def svg_root(width: int, height: int, content: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}">\n'
        f"{content}\n"
        f"</svg>"
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

    print(f"Generated assets in: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
