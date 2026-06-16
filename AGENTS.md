# Agent Notes for p5-skin

A Persona 5 inspired fcitx5 input method skin.

## Project layout

```text
p5-skin/
├── dist/p5-phantom-skin/    # Installable fcitx5 theme (theme.conf + SVGs)
├── scripts/generate_assets.py # Parameterized SVG generator
├── docs/IMPLEMENTATION.md     # Implementation plan
├── README.md
└── LICENSE
```

## How to generate assets

```bash
python scripts/generate_assets.py
```

Output goes to `dist/p5-phantom-skin/`.

## How to install and test

```bash
# Copy theme to fcitx5 user themes
mkdir -p ~/.local/share/fcitx5/themes/
cp -r dist/p5-phantom-skin ~/.local/share/fcitx5/themes/

# Set theme in fcitx5 config
# ~/.config/fcitx5/conf/classicui.conf
# Theme=P5 Phantom
# DarkTheme=P5 Phantom

# Restart fcitx5
fcitx5 -r
```

## Fonts

The skin does not bundle fonts. For a P5-like look install `p5hatty` locally
(only free for personal use; do not commit it to the repo). Chinese text falls
back to the system CJK font configured in `classicui.conf`.

## What not to commit

See `.gitignore`. Reference images, screenshots, font files, and Python caches
are excluded.
