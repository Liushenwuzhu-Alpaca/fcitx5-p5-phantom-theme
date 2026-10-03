#!/usr/bin/env python3
"""Generate Persona 5 style SVG assets for the fcitx5 skin.

All coordinates and colors are parameterized so the theme can be tuned
without hand-editing SVG files.

Design: "怪盗指令" (Command). A skewed black tag with a thick white
outline, an offset crimson slab behind it, and a halftone decal in the
bottom-right corner. Selected candidates flip to a white tag with black
text, backed by a small offset red slab.

Geometry rules, because fcitx5 stretches 9-patch edges and centers:
every shape keeps purely horizontal or purely vertical boundaries at the
margin splits, so slanted ends stay inside the fixed corner tiles.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class Palette:
    black: str = "#000000"
    crimson: str = "#E5191C"
    dark_red: str = "#A31417"
    bright_red: str = "#FF2B2B"
    white: str = "#ffffff"
    grey: str = "#bdbdbd"
    dim_grey: str = "#5a5a5a"
    yellow: str = "#f2e852"


PALETTE = Palette()


@dataclass(frozen=True)
class PanelGeometry:
    """Canvas size, 9-patch margins and the stacked slab offsets.

    fcitx5 scales each 9-patch tile independently: the top/bottom strips are
    scaled vertically, the left/right strips horizontally, the center in both
    axes, and the four corners not at all. Every slab below therefore keeps
    horizontal top/bottom edges, so scaling only changes a slab's height or
    width, never the shape of its slanted end caps.
    """

    # Canvas and 9-patch margins (must match theme.conf).
    width: int = 460
    height: int = 72
    margin_left: int = 24
    margin_right: int = 26
    margin_top: int = 14
    margin_bottom: int = 18
    # Slanted end caps: how far a slab's bottom edge trails its top edge.
    skew: float = 12.0
    # Crimson backing slab: lower and further right, so it peeks out there.
    red: tuple[float, float, float, float] = (3.0, 2.0, 457.0, 66.0)
    # White outline slab.
    white: tuple[float, float, float, float] = (6.0, 6.0, 453.0, 62.0)
    # Black core slab, the text area.
    black: tuple[float, float, float, float] = (10.0, 10.0, 450.0, 54.0)
    # Crimson pinstripe along the lower edge of the black slab.
    pinstripe_offset: float = 8.0
    pinstripe_h: float = 2.0


PANEL = PanelGeometry()


def svg_root(width: float, height: float, content: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width:g} {height:g}" width="{width:g}" height="{height:g}">\n'
        f"{content}\n"
        f"</svg>"
    )


def svg_slab(rect: tuple[float, float, float, float], skew: float, fill: str) -> str:
    """Emit one slab: a rectangle whose bottom edge trails left by `skew`."""
    left, top, right, bottom = rect
    points = (
        (left, top),
        (right, top),
        (right - skew, bottom),
        (left - skew, bottom),
    )
    path = " ".join(f"{x:g},{y:g}" for x, y in points)
    return f'  <polygon points="{path}" fill="{fill}"/>\n'


def generate_panel(geometry: PanelGeometry = PANEL) -> str:
    """Input panel background: crimson backing, white outline, black core."""
    g = geometry
    p = PALETTE

    red, white, black = g.red, g.white, g.black

    content = svg_slab(red, g.skew, p.crimson)
    content += svg_slab(white, g.skew, p.white)
    content += svg_slab(black, g.skew, p.black)
    content += svg_slab(
        (
            black[0],
            black[3] - g.pinstripe_offset - g.pinstripe_h,
            black[2],
            black[3] - g.pinstripe_offset,
        ),
        g.skew,
        p.crimson,
    )
    return svg_root(g.width, g.height, content)


def generate_highlight(
    width: int = 132,
    height: int = 30,
    skew: float = 8.0,
    margin_left: int = 10,
    margin_right: int = 12,
) -> str:
    """Candidate highlight: white tag over a crimson backing slab.

    Same stacking as the panel, in miniature. The slanted caps sit inside the
    left/right margin columns and the stretched center is flat bands.
    """
    del margin_left, margin_right
    p = PALETTE
    red = (2.0, 2.0, width - 2.0, height - 4.0)
    white = (4.0, 4.0, width - 6.0, height - 6.0)
    content = svg_slab(red, skew, p.crimson)
    content += svg_slab(white, skew, p.white)
    return svg_root(width, height, content)



def generate_halftone(
    width: int = 120,
    height: int = 40,
    color: str = PALETTE.crimson,
    opacity: float = 0.45,
    step: float = 6.0,
    max_radius: float = 2.6,
) -> str:
    """Halftone dot decal used as the panel overlay.

    Fixed-size decal, never stretched: hexagon packing, dot radius fading
    toward the top-left corner.
    """
    dots: list[str] = []
    row = 0
    y = step / 2
    while y < height:
        x = step / 2 + (row % 2) * (step / 2)
        while x < width:
            dx = x / width
            dy = y / height
            t = 1.0 - min(1.0, (dx * dx + dy * dy) ** 0.5 / 1.05)
            r = max_radius * t
            if r > 0.45:
                dots.append(f'    <circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}"/>')
            x += step
        y += step
        row += 1
    body = (
        f'  <g fill="{color}" fill-opacity="{opacity:g}">\n'
        + "\n".join(dots)
        + "\n  </g>\n"
    )
    return svg_root(width, height, body)


def generate_arrow(direction: str, size: float = 30.0) -> str:
    """Page button: a white wedge with a crimson drop shadow."""
    p = PALETTE
    w = size
    h = size * 1.08
    half = h / 2
    if direction == "next":
        pts = [(4.0, 3.0), (w - 3.0, half), (4.0, h - 3.0)]
    else:
        pts = [(w - 4.0, 3.0), (3.0, half), (w - 4.0, h - 3.0)]
    shadow = " ".join(f"{x + 2.5:g},{y + 2.5:g}" for x, y in pts)
    body = " ".join(f"{x:g},{y:g}" for x, y in pts)
    content = (
        f'  <polygon points="{shadow}" fill="{p.crimson}"/>\n'
        f'  <polygon points="{body}" fill="{p.white}"/>\n'
    )
    return svg_root(w, h, content)


THEME_CONF = f"""[Metadata]
Name=P5 Phantom
Version=2
Author=OpenCode
Description=A fcitx5 skin inspired by the visual style of Persona 5
ScaleWithDPI=True

[InputPanel]
NormalColor={PALETTE.white}ff
CandidateLabelColor={PALETTE.bright_red}ff
HighlightCandidateColor={PALETTE.black}ff
HighlightCandidateLabelColor={PALETTE.crimson}ff
CandidateCommentColor={PALETTE.grey}ff
HighlightCandidateCommentColor={PALETTE.dim_grey}ff
HighlightColor={PALETTE.white}ff
HighlightBackgroundColor=#00000000
Spacing=4

[InputPanel/Background]
Image=panel.svg
Color={PALETTE.black}ff
BorderColor={PALETTE.crimson}ff
BorderWidth=0
Overlay=halftone.svg
Gravity=BottomRight
OverlayOffsetX=44
OverlayOffsetY=22

[InputPanel/Background/Margin]
Left={PANEL.margin_left}
Right={PANEL.margin_right}
Top={PANEL.margin_top}
Bottom={PANEL.margin_bottom}

[InputPanel/Background/OverlayClipMargin]
Left=24
Right=26
Top=14
Bottom=18

[InputPanel/Highlight]
Image=highlight.svg
Color={PALETTE.crimson}ff
BorderColor=#00000000

[InputPanel/Highlight/Margin]
Left=10
Right=12
Top=4
Bottom=4

[InputPanel/TextMargin]
Left=6
Right=8
Top=4
Bottom=4

[InputPanel/ContentMargin]
Left=20
Right=24
Top=14
Bottom=18

[InputPanel/BlurMargin]
Left=16
Right=16
Top=16
Bottom=16

[InputPanel/PrevPage]
Image=prev.svg

[InputPanel/NextPage]
Image=next.svg

[Menu]
NormalColor={PALETTE.white}ff
HighlightCandidateColor={PALETTE.black}ff
Spacing=4

[Menu/Separator]
Color={PALETTE.crimson}ff
"""


def write_asset(directory: Path, name: str, content: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(content, encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate Persona 5 style fcitx5 skin assets."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dist" / "p5-phantom-skin",
        help="Output directory for generated assets.",
    )
    parser.add_argument(
        "--no-conf",
        action="store_true",
        help="Only write SVGs, leave theme.conf untouched.",
    )
    args = parser.parse_args(argv)

    out = args.out
    write_asset(out, "panel.svg", generate_panel())
    write_asset(out, "highlight.svg", generate_highlight())
    write_asset(out, "halftone.svg", generate_halftone())
    write_asset(out, "prev.svg", generate_arrow("prev"))
    write_asset(out, "next.svg", generate_arrow("next"))
    if not args.no_conf:
        write_asset(out, "theme.conf", THEME_CONF)

    print(f"Generated assets in: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
