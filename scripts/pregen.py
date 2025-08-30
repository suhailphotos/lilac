#!/usr/bin/env python3
"""
pregen.py
Create a lilac <palette>.yml from a terminal.sexy JSON, expanding ANSI hues
into Catppuccin's wider override set using variables like @ansi[5], blend(...),
@fg, @bg, etc. Neutrals come from Catppuccin (variant) if available.

Examples:
  python scripts/pregen.py \
    --id lilac-pearlbloom --label Pearlbloom --variant latte \
    --in palettes/lilac-pearlbloom-termsexy_2025-08-29_16-48-22.json \
    --out palettes/lilac-pearlbloom.yml

  python scripts/pregen.py \
    --id lilac-nightbloom --label Nightbloom --variant mocha \
    --in palettes/lilac-nightbloom-termsexy_2025-08-28_23-22-33.json \
    --out palettes/lilac-nightbloom.yml
"""
from __future__ import annotations
import argparse, json, os, sys, urllib.request
from typing import Dict, Any, List

CATPP_JSON_URL = "https://raw.githubusercontent.com/catppuccin/palette/refs/heads/main/palette.json"
CAT_NEUTRAL_ORDER = [
    "text","subtext1","subtext0","overlay2","overlay1","overlay0",
    "surface2","surface1","surface0","base","mantle","crust",
]
CAT_HUE_ORDER = [
    "rosewater","flamingo","pink","mauve","red","maroon","peach","yellow",
    "green","teal","sky","sapphire","blue","lavender",
]

def read_json(path: str) -> Dict[str, Any]:
    if path == "-":
        return json.loads(sys.stdin.read())
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_catppuccin_palette(src: str) -> Dict[str, Any]:
    try:
        if src.startswith("http://") or src.startswith("https://"):
            with urllib.request.urlopen(src) as r:
                return json.loads(r.read().decode("utf-8"))
        with open(src, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def latte_or_mocha_set(palette: Dict[str, Any], variant: str) -> Dict[str,str]:
    v = palette.get(variant, {}) if palette else {}
    colors = v.get("colors", {})
    out = {}
    for name, spec in colors.items():
        if isinstance(spec, dict) and "hex" in spec:
            out[name] = spec["hex"].lower()
    return out

def detect_cursor_text(bg_hex: str) -> str:
    # Pick black/white for cursor text based on background luminance
    h = bg_hex.lstrip("#")
    if len(h) != 6: return "#000000"
    r,g,b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    # sRGB → relative luminance-ish
    lum = (0.2126*(r/255.0)) + (0.7152*(g/255.0)) + (0.0722*(b/255.0))
    return "#000000" if lum > 0.6 else "#ffffff"

def yaml_quote(hex_or_token: str) -> str:
    # always quote to be safe in YAML
    return f"\"{hex_or_token}\""

def main():
    ap = argparse.ArgumentParser(description="terminal.sexy → lilac palette YAML (with variables)")
    ap.add_argument("--in", dest="in_path", required=True, help="terminal.sexy JSON")
    ap.add_argument("--id", required=True, help="palette id (e.g., lilac-pearlbloom)")
    ap.add_argument("--label", required=True, help="human label (e.g., Pearlbloom)")
    ap.add_argument("--variant", choices=["latte","frappe","macchiato","mocha"], required=True)
    ap.add_argument("--comment", default="", help="optional comment color hex (else leave empty)")
    ap.add_argument("--catpp", default=CATPP_JSON_URL, help="Catppuccin palette.json path/URL")
    ap.add_argument("--out", required=True, help="output YAML path")
    args = ap.parse_args()

    js = read_json(args.in_path)
    colors: List[str] = js.get("color") or js.get("colors")
    if not isinstance(colors, list) or len(colors) != 16:
        print("Input must have 16 colors in 'color'.", file=sys.stderr); sys.exit(2)
    fg = js.get("foreground") or "#ffffff"
    bg = js.get("background") or "#000000"
    cursor = js.get("cursor") or fg
    cursor_text = js.get("cursor_text") or detect_cursor_text(bg)
    sel_bg = js.get("selection_background")
    sel_fg = js.get("selection_foreground")

    cat = fetch_catppuccin_palette(args.catpp)
    base = latte_or_mocha_set(cat, args.variant)

    # --- Build YAML text ---
    lines = []
    lines.append(f"id: {args.id}")
    lines.append(f"label: {args.label}")
    lines.append(f"variant: {args.variant}  # Catppuccin base")
    if args.comment:
        lines.append(f"comment: {yaml_quote(args.comment)}")
    lines.append("")
    lines.append("terminal:")
    lines.append("  colors:")
    for i, hx in enumerate(colors):
        lines.append(f"    - {yaml_quote(hx)}  # {i}")
    lines.append(f"  background: {yaml_quote(bg)}")
    lines.append(f"  foreground: {yaml_quote(fg)}")
    lines.append(f"  cursor:     {yaml_quote(cursor)}")
    lines.append(f"  cursor_text: {yaml_quote(cursor_text)}")
    if sel_bg: lines.append(f"  selection_background: {yaml_quote(sel_bg)}")
    if sel_fg: lines.append(f"  selection_foreground: {yaml_quote(sel_fg)}")
    lines.append("")
    lines.append("catppuccin_overrides:")

    # --- Hue expansion using variables & blends ---
    # ANSI mapping by convention: 1=red,2=green,3=yellow,4=blue,5=magenta,6=cyan,
    # bright variants: 9,10,11,12,13,14.
    var = lambda s: yaml_quote(s)
    blend = lambda a,b,t: yaml_quote(f"blend({a}, {b}, {t})")

    # Pinks/Magentas
    lines.append(f"  pink:       {var('@ansi[5]')}    # from ANSI 5 (magenta)")
    lines.append(f"  mauve:      {var('@ansi[13]')}   # bright magenta")
    lines.append(f"  lavender:   {blend('@ansi[5]','@ansi[4]','0.50')}  # mid magenta↔blue")

    # Reds/Oranges/Yellows
    lines.append(f"  red:        {var('@ansi[1]')}    # ANSI 1 (red)")
    lines.append(f"  maroon:     {var('@ansi[9]')}    # bright red")
    lines.append(f"  yellow:     {var('@ansi[3]')}    # ANSI 3 (yellow/brown)")
    lines.append(f"  peach:      {blend('@ansi[1]','@ansi[3]','0.50')}  # red↔yellow mix")

    # Greens/Teals/Cyans/Blues
    lines.append(f"  green:      {var('@ansi[2]')}    # ANSI 2 (green/teal)")
    lines.append(f"  teal:       {var('@ansi[6]')}    # ANSI 6 (cyan)")
    lines.append(f"  sky:        {var('@ansi[12]')}   # bright blue")
    lines.append(f"  sapphire:   {blend('@ansi[6]','@ansi[4]','0.50')}  # cyan↔blue mix")
    lines.append(f"  blue:       {var('@ansi[4]')}    # ANSI 4 (blue)")

    # Keep neutrals from Catppuccin variant (best legibility), if available
    if base:
        for k in CAT_NEUTRAL_ORDER:
            if k in base:
                lines.append(f"  {k}:       {yaml_quote(base[k])}")
    else:
        # Fallback: omit neutrals so you can fill later
        pass

    lines.append("")
    lines.append("tmux:")
    lines.append("  # Feel free to tune these later")
    lines.append("  status_fg: \"@ansi[7]\"")
    lines.append("  status_bg: \"@ansi[8]\"")
    lines.append("  message_fg: \"@fg\"")
    lines.append("  message_bg: \"@ansi[8]\"")
    lines.append("  pane_border: \"@ansi[8]\"")
    lines.append("  pane_active_border: \"@ansi[12]\"")
    lines.append("")
    lines.append("highlights: {}")
    lines.append("")

    out = os.path.expanduser(os.path.expandvars(args.out))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
