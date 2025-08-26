# Lilac

A cozy purple-leaning theme family for **Neovim**, **tmux**, **Ghostty**, and **iTerm** — Catppuccin-powered.

## Flavors
- `lilac-nightbloom` — dark / high-contrast
- `lilac-mistbloom` — soft / slate
- (future) `lilac-emberbloom` — warm dark
- (future) `lilac-pearlbloom` — light

## Layout (generated + hand-authored)
```
/ (repo root)
├─ palettes/          # YAML source of truth (lilac-*.yml)
├─ tools/             # generators (e.g., gen.py)
├─ colors/            # Neovim colorschemes (generated)
├─ lua/lilac/         # Neovim theme module (generated + hand)
├─ plugin/            # Neovim commands (hand)
├─ tmux/              # tmux theme file(s) (generated)
├─ ghostty/themes/    # Ghostty pallets (generated)
└─ iterm/             # .itermcolors (generated)
```

## Quick start (later)
- Edit palettes in `palettes/`
- Run generator to produce Nvim/tmux/Ghostty/iTerm files
- Load the Nvim theme via lazy.nvim and `:colorscheme lilac-nightbloom`
