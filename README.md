# Lilac

A cozy purple-leaning theme family for terminals, editors, and desktop applications.

## Flavors
- `lilac-nightbloom` — dark / high-contrast
- `lilac-mistbloom` — soft / slate
- `lilac-pearlbloom` — light
- `lilac-emberbloom` — reserved for a future warm-dark flavor

## Layout (generated + hand-authored)
```
/ (repo root)
├─ palettes/          # YAML source of truth (lilac-*.yml)
├─ tools/             # generators (e.g., gen.py)
├─ colors/            # Neovim colorschemes (generated)
├─ lua/lilac/         # Neovim theme module (generated + hand)
├─ plugin/            # Neovim commands (hand)
├─ tmux/              # tmux theme file(s) (generated)
├─ ghostty/themes/    # Ghostty palettes (generated)
├─ blink/themes/      # Blink themes
├─ iterm/             # .itermcolors (generated)
├─ typora/themes/     # Typora application themes
└─ keybar/            # Keybar theme
```

## Quick start (later)
- Edit palettes in `palettes/`
- Run generator to produce Nvim/tmux/Ghostty/iTerm files
- Load the Nvim theme via lazy.nvim and `:colorscheme lilac-nightbloom`
