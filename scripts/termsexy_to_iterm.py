#!/usr/bin/env python3
"""
terminal.sexy JSON -> iTerm2 .itermcolors

Usage:
  # Single palette (reads file or '-' for stdin) → single .itermcolors
  python scripts/termsexy_to_iterm.py palettes/lilac-pearlbloom-termsexy_*.json \
    -o iterm/lilac-pearlbloom.itermcolors

  # From stdin
  cat palettes/lilac-pearlbloom-termsexy_*.json | \
    python scripts/termsexy_to_iterm.py - > iterm/lilac-pearlbloom.itermcolors

  # Two palettes (light + dark) → combined .itermcolors with Light/Dark sets
  python scripts/termsexy_to_iterm.py \
    --light palettes/lilac-pearlbloom-termsexy_*.json \
    --dark  palettes/lilac-nightbloom-termsexy_*.json \
    -o iterm/lilac-combined.itermcolors

  # Positional form also works (order: LIGHT DARK)
  python scripts/termsexy_to_iterm.py palettes/light.json palettes/dark.json -o out.itermcolors
"""
from __future__ import annotations
import argparse, json, plistlib, sys, os
from typing import Dict, Any, List, Optional, Tuple

def _read_json(path: str) -> Dict[str, Any]:
    if path == "-":
        data = sys.stdin.read()
        return json.loads(data)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _hex_to_rgb_f(hexstr: str) -> Tuple[float, float, float]:
    s = hexstr.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch*2 for ch in s)
    if len(s) != 6:
        raise ValueError(f"Bad hex color: {hexstr}")
    r = int(s[0:2], 16) / 255.0
    g = int(s[2:4], 16) / 255.0
    b = int(s[4:6], 16) / 255.0
    return (r, g, b)

def _plist_color(hexstr: str, color_space: str = "sRGB", alpha: float = 1.0) -> Dict[str, Any]:
    r, g, b = _hex_to_rgb_f(hexstr)
    return {
        "Red Component": r,
        "Green Component": g,
        "Blue Component": b,
        "Alpha Component": float(alpha),
        "Color Space": color_space,
    }

def _normalize_termsexy(js: Dict[str, Any]) -> Dict[str, Any]:
    """
    terminal.sexy json looks like:
      {
        "color": ["#...", ... x16],
        "foreground": "#...",
        "background": "#...",
        (optionals like "cursor", etc may be absent)
      }
    """
    colors = js.get("color") or js.get("colors")
    if not isinstance(colors, list) or len(colors) != 16:
        raise ValueError("terminal.sexy json must contain 16-color 'color' list")
    out = {
        "colors": colors,
        "foreground": js.get("foreground"),
        "background": js.get("background"),
        "cursor": js.get("cursor") or js.get("cursorColor"),
        "cursor_text": js.get("cursor_text") or js.get("cursorText") or js.get("cursor_text_color"),
        "selection_background": js.get("selection_background") or js.get("selectionBackground"),
        "selection_foreground": js.get("selection_foreground") or js.get("selectionForeground"),
    }
    return out

# ----- emitters --------------------------------------------------------------

ANSI_KEYS = [f"Ansi {i} Color" for i in range(16)]

EXTRAS_MAP = {
    "Foreground Color": "foreground",
    "Background Color": "background",
    "Cursor Color": "cursor",
    "Cursor Text Color": "cursor_text",
    "Selection Color": "selection_background",
    "Selected Text Color": "selection_foreground",
}

def _emit_single(pl: Dict[str, Any], color_space: str) -> Dict[str, Any]:
    """Emit a plain .itermcolors dict from one palette."""
    d: Dict[str, Any] = {}
    for i, hx in enumerate(pl["colors"]):
        d[ANSI_KEYS[i]] = _plist_color(hx, color_space)
    # If optional fields missing, fall back to reasonable defaults
    fg = pl.get("foreground") or "#ffffff"
    bg = pl.get("background") or "#000000"
    cur = pl.get("cursor") or fg
    cur_txt = pl.get("cursor_text") or bg
    sel_bg = pl.get("selection_background")
    sel_fg = pl.get("selection_foreground")

    d["Foreground Color"] = _plist_color(fg, color_space)
    d["Background Color"] = _plist_color(bg, color_space)
    d["Cursor Color"] = _plist_color(cur, color_space)
    d["Cursor Text Color"] = _plist_color(cur_txt, color_space)
    if sel_bg: d["Selection Color"] = _plist_color(sel_bg, color_space)
    if sel_fg: d["Selected Text Color"] = _plist_color(sel_fg, color_space)
    return d

def _emit_combined(light: Dict[str, Any], dark: Dict[str, Any], color_space: str) -> Dict[str, Any]:
    """
    Combined plist:
      - Plain keys use the LIGHT palette as a fallback.
      - Also writes '(Light)' and '(Dark)' variants for each key.
    """
    d = _emit_single(light, color_space)

    # Add Light/Dark variants for ANSI 0..15
    for i in range(16):
        d[f"Ansi {i} Color (Light)"] = _plist_color(light["colors"][i], color_space)
        d[f"Ansi {i} Color (Dark)"]  = _plist_color(dark["colors"][i],  color_space)

    # Add Light/Dark for extras (use fallbacks same as _emit_single)
    def pick(pl: Dict[str, Any], key: str, default: Optional[str]) -> str:
        v = pl.get(key)
        return v if v else (default if default else "#000000")

    # Compute the base defaults for each palette
    l_fg = pick(light, "foreground", "#ffffff")
    l_bg = pick(light, "background", "#000000")
    d_fg = pick(dark,  "foreground", "#ffffff")
    d_bg = pick(dark,  "background", "#000000")

    pairs = [
        ("Foreground Color", l_fg, d_fg),
        ("Background Color", l_bg, d_bg),
        ("Cursor Color",     pick(light, "cursor", l_fg), pick(dark, "cursor", d_fg)),
        ("Cursor Text Color",pick(light, "cursor_text", l_bg), pick(dark, "cursor_text", d_bg)),
    ]

    # Optional selection colors
    if light.get("selection_background") or dark.get("selection_background"):
        pairs.append(("Selection Color",
                      pick(light, "selection_background", l_bg),
                      pick(dark,  "selection_background", d_bg)))
    if light.get("selection_foreground") or dark.get("selection_foreground"):
        pairs.append(("Selected Text Color",
                      pick(light, "selection_foreground", l_fg),
                      pick(dark,  "selection_foreground", d_fg)))

    for base_key, l_hex, d_hex in pairs:
        # plain key already written from LIGHT via _emit_single(light)
        d[f"{base_key} (Light)"] = _plist_color(l_hex, color_space)
        d[f"{base_key} (Dark)"]  = _plist_color(d_hex, color_space)

    return d

# ----- CLI -------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Convert terminal.sexy JSON to iTerm .itermcolors")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--light", help="Path to LIGHT terminal.sexy JSON (or '-' for stdin)")
    g.add_argument("--single", help="Alias for --light when converting one file")
    ap.add_argument("--dark", help="Path to DARK terminal.sexy JSON (optional)")
    ap.add_argument("positional", nargs="*", help="Optionally pass LIGHT [DARK] as positionals")
    ap.add_argument("-o", "--out", help="Write to this path. If omitted, prints to stdout.")
    ap.add_argument("--color-space", default="sRGB", choices=["sRGB", "P3"],
                    help="Color space tag to write in the plist (default: sRGB)")
    args = ap.parse_args()

    light_path = args.light or args.single
    dark_path = args.dark

    # Allow positional LIGHT [DARK]
    if not light_path and args.positional:
        light_path = args.positional[0]
        if len(args.positional) > 1:
            dark_path = args.positional[1]

    if not light_path:
        ap.error("Provide a LIGHT palette (file or '-') as --light/--single or positional.")

    try:
        light_raw = _read_json(light_path)
        light = _normalize_termsexy(light_raw)
        if dark_path:
            dark_raw = _read_json(dark_path)
            dark = _normalize_termsexy(dark_raw)
            plist_dict = _emit_combined(light, dark, args.color_space)
        else:
            plist_dict = _emit_single(light, args.color_space)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if args.out:
        out_path = os.path.expanduser(os.path.expandvars(args.out))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            plistlib.dump(plist_dict, f)
        print(f"Wrote {out_path}")
    else:
        # Write to stdout as binary plist
        plistlib.dump(plist_dict, sys.stdout.buffer)

if __name__ == "__main__":
    main()
