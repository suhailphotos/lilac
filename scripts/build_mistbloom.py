#!/usr/bin/env python3
"""
build_mistbloom.py
Generate a Lilac palette YAML using Catppuccin Latte + XcodeLightHC ANSI colors.

Usage:
  python build_mistbloom.py --out /path/to/mistbloom.yaml
  # or print to stdout:
  python build_mistbloom.py
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.request
from typing import Dict, Any

CATPPUCCIN_URL = "https://raw.githubusercontent.com/catppuccin/palette/refs/heads/main/palette.json"

# Xcode Light High Contrast — 16 ANSI colors (0..15)
# Source: lunacookies/vim-colors-xcode README (Light High Contrast Palette)
# Order: [black, red, green, yellow, blue, magenta, cyan, white] + bright variants
XCODE_LIGHT_HC_ANSI = [
    "#b4d8fd",  # 0  black
    "#ad1805",  # 1  red
    "#355d61",  # 2  green
    "#78492a",  # 3  yellow
    "#0058a1",  # 4  blue
    "#9c2191",  # 5  magenta
    "#703daa",  # 6  cyan
    "#000000",  # 7  white
    "#8a99a6",  # 8  br_black
    "#ad1805",  # 9  br_red
    "#174145",  # 10 br_green
    "#78492a",  # 11 br_yellow
    "#003f73",  # 12 br_blue
    "#9c2191",  # 13 br_magenta
    "#441ea1",  # 14 br_cyan
    "#000000",  # 15 br_white
]

# The order we’ll print Catppuccin overrides, matching your example
CATPP_KEYS = [
    "rosewater","flamingo","pink","mauve","red","maroon","peach","yellow",
    "green","teal","sky","sapphire","blue","lavender",
    "text","subtext1","subtext0","overlay2","overlay1","overlay0",
    "surface2","surface1","surface0","base","mantle","crust",
]

def fetch_json(src: str) -> Dict[str, Any]:
    if src.startswith("http://") or src.startswith("https://"):
        with urllib.request.urlopen(src) as r:
            return json.loads(r.read().decode("utf-8"))
    with open(src, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_latte_colors(palette: Dict[str, Any]) -> Dict[str, str]:
    latte = palette.get("latte", {})
    colors = latte.get("colors", {})
    out: Dict[str, str] = {}
    for name, spec in colors.items():
        hexval = spec.get("hex")
        if isinstance(hexval, str):
            out[name] = hexval.lower()
    return out

def yaml_escape(s: str) -> str:
    # Always quote hex strings
    return f"\"{s}\"" if s.startswith("#") else s

def build_yaml(latte: Dict[str, str]) -> str:
    # Terminal UI fields — favor Latte neutrals for UI; ANSI list from Xcode Light HC
    background = latte.get("base", "#ffffff")        # latte base
    foreground = latte.get("text", "#000000")        # latte text
    cursor      = latte.get("rosewater", "#dc8a78")  # pleasant cursor
    cursor_text = latte.get("crust", "#dce0e8")      # text color inside cursor
    sel_bg      = latte.get("surface1", latte.get("overlay1", "#bcc0cc"))
    sel_fg      = latte.get("text", "#000000")

    lines = []
    lines.append(f"id: lilac-mistbloom")
    lines.append(f"label: Mistbloom")
    lines.append(f"variant: latte  # Catppuccin base")
    lines.append("")
    lines.append("terminal:")
    lines.append("  colors:")
    for i, hx in enumerate(XCODE_LIGHT_HC_ANSI):
        lines.append(f"    - {yaml_escape(hx)}  # {i}")
    lines.append(f"  background: {yaml_escape(background)}")
    lines.append(f"  foreground: {yaml_escape(foreground)}")
    lines.append(f"  cursor:     {yaml_escape(cursor)}")
    lines.append(f"  cursor_text: {yaml_escape(cursor_text)}")
    lines.append(f"  selection_background: {yaml_escape(sel_bg)}")
    lines.append(f"  selection_foreground: {yaml_escape(sel_fg)}")
    lines.append("")
    lines.append("catppuccin_overrides:")

    # Print overrides in a stable, friendly order; include only keys present
    for k in CATPP_KEYS:
        if k in latte:
            lines.append(f"  {k}:      {yaml_escape(latte[k])}")

    # If Latte has any extra keys not in CATPP_KEYS, append them at the end
    extras = [k for k in latte.keys() if k not in CATPP_KEYS]
    for k in sorted(extras):
        lines.append(f"  {k}:      {yaml_escape(latte[k])}")

    return "\n".join(lines) + "\n"

def main():
    ap = argparse.ArgumentParser(description="Build Lilac Mistbloom YAML from Catppuccin Latte.")
    ap.add_argument("--palette", default=CATPPUCCIN_URL,
                    help="Path or URL to Catppuccin palette.json (default: official URL).")
    ap.add_argument("--out", help="Write YAML to this file. If omitted, prints to stdout.")
    args = ap.parse_args()

    try:
        palette = fetch_json(args.palette)
    except Exception as e:
        print(f"ERROR: failed to load palette: {e}", file=sys.stderr)
        sys.exit(1)

    latte = extract_latte_colors(palette)
    if not latte:
        print("ERROR: Latte colors not found in palette JSON.", file=sys.stderr)
        sys.exit(2)

    out_text = build_yaml(latte)

    if args.out:
        out_path = os.path.expandvars(os.path.expanduser(args.out))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(out_text)
        print(f"Wrote {out_path}")
    else:
        sys.stdout.write(out_text)

if __name__ == "__main__":
    main()
