# Lilac for Typora

Lilac themes for Typora, based on Typora's GitHub theme structure.

## Themes

- `lilac-nightbloom.css`
- `lilac-pearlbloom.css`

## Typography

| Role | Font |
|---|---|
| Body | SF Pro Text |
| Headings and interface | SF Pro Display |
| Inline and fenced code | SF Mono |

Fallback system fonts are included when the preferred fonts are unavailable.

## Application surfaces

Typora uses neutral application surfaces rather than the terminal background
colors from the corresponding Lilac palette.

### Nightbloom

| Role | Value |
|---|---|
| Document background | `#1d1d1d` |
| Code and passive frames | `#212121` |
| Main text | `#e8e6f7` |
| Muted text | `#817d98` |
| Frame radius | `4px` |

### Pearlbloom

| Role | Value |
|---|---|
| Document background | `#ffffff` |
| Code and passive frames | `#f8f8f8` |
| Frame radius | `4px` |

Lilac palette colors remain in use for headings, links, selections, syntax
highlighting, status colors, and other semantic accents.

## Install on macOS

From the repository root:

```bash
./scripts/install_typora_themes.py
