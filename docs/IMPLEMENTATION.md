# Implementation Plan: Persona 5 Style Fcitx5 Skin

## Goal

Build a fcitx5 input method skin inspired by the visual style of *Persona 5*.

- Primary palette: black background + crimson red `#E5191C` + white
- Panel: skewed black tag with a thick white outline and an offset crimson
  backing slab ("怪盗指令" / Command)
- Highlight: white skewed tag with black text over a small crimson slab
- Overlay decals (halftone dots, page-button shadows) stay fixed-size
- All assets are original SVG to avoid copyright issues

## Project Structure

```text
p5-skin/
├── README.md
├── LICENSE
├── scripts/
│   └── generate_assets.py        # Parameterized SVG generator
└── dist/
    └── p5-phantom-skin/          # Final installable skin package
        ├── theme.conf
        ├── panel.svg             # Input panel background (9-patch)
        ├── highlight.svg         # Candidate highlight background
        ├── halftone.svg          # Panel overlay decal
        ├── prev.svg              # Previous page button
        └── next.svg              # Next page button
```

## Implementation Steps

### 1. Parameterized SVG Asset Generation

Use `scripts/generate_assets.py` to generate all SVG assets so dimensions,
colors, slab insets and skew amounts can be tuned easily.

Key parameters:

- Canvas size and 9-patch margins (must match `theme.conf` margins)
- Slab rectangles (crimson backing, white outline, black core) and skew
- Pinstripe offset/height inside the black slab
- Halftone dot spacing, radius falloff and opacity

Run the generator:

```bash
python scripts/generate_assets.py
```

Output goes to `dist/p5-phantom-skin/`. `theme.conf` is written alongside the
SVGs (pass `--no-conf` to leave an existing `theme.conf` untouched).

### 2. 9-Patch Geometry Rules

fcitx5 scales each 9-patch tile independently: the top/bottom strips scale
vertically, the left/right strips horizontally, the center in both axes, and
the four corners not at all. Sloped edges therefore must live inside the
fixed corner/edge tiles only:

- Every slab keeps horizontal top/bottom edges, so scaling a strip only
  changes a slab's height, never the shape of its slanted end caps.
- Slanted end caps sit inside the left/right margin columns.
- Decorative decals (halftone dots) are Overlays, painted at natural size by
  Gravity/OverlayOffset and clipped by OverlayClipMargin; they never stretch.

### 3. theme.conf Configuration

The generator emits the matching `theme.conf`. Key sections:

- `[InputPanel/Background]` — `panel.svg`, Margin L24 R26 T14 B18,
  `Overlay=halftone.svg` at `Gravity=BottomRight` (44, 22), clipped by
  OverlayClipMargin L24 R26 T14 B18.
- `[InputPanel/Highlight]` — `highlight.svg`, Margin L10 R12 T4 B4 so the
  skewed caps stay in the fixed columns.
- `[InputPanel/TextMargin]` L6 R8 T4 B4 and
  `[InputPanel/ContentMargin]` L20 R24 T14 B18 keep text inside the black
  core slab.
- `[InputPanel/PrevPage]` / `[InputPanel/NextPage]` — white wedge buttons
  with a crimson drop shadow.
- Colors: normal text white, labels bright red `#FF2B2B`, selected candidate
  black on the white tag, selected label crimson.

### 4. SVG Design Specs

#### panel.svg (input panel background)

- Canvas: 460x72 px
- Crimson backing slab (3, 2)-(448, 66), white outline (6, 6)-(441, 62),
  black core (10, 10)-(438, 54); bottom edges trail right by 12 px so the
  left edges stay vertical and nothing leaves the canvas
- Crimson pinstripe inside the black core, 8 px above its bottom edge
- Margin: L24 R26 T14 B18; the slant lives entirely in the right column

#### highlight.svg (candidate highlight)

- Canvas: 132x30 px
- Crimson slab (2, 2)-(122, 26) behind a white tag (4, 4)-(118, 24),
  bottom edges trailing right by 8 px
- Margin: L10 R12 T4 B4; the slant lives entirely in the right column

#### halftone.svg (panel overlay)

- Canvas: 120x40 px, hexagon-packed dots whose radius fades toward the
  top-left; crimson at 45% opacity

#### prev.svg / next.svg

- 28x30 px white wedge with a crimson shadow offset by 2.5 px

## Technical Notes

1. **9-patch margins must match the SVG design**
   `[Background/Margin]` in `theme.conf` defines the unstretchable regions;
   slanted caps must sit inside them or stretching will deform them.

2. **SVG is preferred over PNG**
   Scales cleanly on HiDPI displays. fcitx5 supports SVG backgrounds.

3. **Fonts are not bundled in the skin**
   fcitx5 fonts are configured in `~/.config/fcitx5/conf/classicui.conf`.
   The README recommends a heavy sans (e.g. Noto Sans CJK SC Bold); users
   may install `p5hatty` themselves for personal use (do not commit it).

4. **Only one overlay per background**
   fcitx5 supports a single `Overlay=` per Background and per Highlight, so
   decals are consolidated into one SVG each.

## Development Workflow

```bash
# 1. Generate or tweak assets
python scripts/generate_assets.py

# 2. Install locally for testing
mkdir -p ~/.local/share/fcitx5/themes/
cp -r dist/p5-phantom-skin ~/.local/share/fcitx5/themes/
fcitx5 -r

# 3. Switch theme in fcitx5-configtool and inspect

# 4. Iterate
# Edit scripts/generate_assets.py, regenerate, copy, and restart fcitx5
```

## Copyright and Licensing

- Project license: **MIT**
- README must include a `fan-made, not affiliated with Atlus/SEGA` disclaimer.
- All SVG assets are generated by the project's own script.
- Do not include the P5 Hatty font file; point users to install it themselves
  for personal use.
