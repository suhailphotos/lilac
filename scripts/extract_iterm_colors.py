#!/usr/bin/env python3
import sys, plistlib, pathlib

def plist_color_to_hex(c):
    # iTerm stores floats 0..1
    r = int(round(c.get('Red Component',   0.0) * 255))
    g = int(round(c.get('Green Component', 0.0) * 255))
    b = int(round(c.get('Blue Component',  0.0) * 255))
    return f"#{r:02x}{g:02x}{b:02x}"

def main(path):
    p = pathlib.Path(path)
    with p.open('rb') as f:
        data = plistlib.load(f)

    def get(name):
        v = data.get(name)
        return plist_color_to_hex(v) if isinstance(v, dict) else "(missing)"

    out = {
        "ansi0":       get("Ansi 0 Color"),
        "ansi8":       get("Ansi 8 Color"),
        "background":  get("Background Color"),
        "foreground":  get("Foreground Color"),
        "cursor":      get("Cursor Color"),
        "cursor_text": get("Cursor Text Color"),
    }

    print(f"Preset: {path}")
    for k, v in out.items():
        print(f"{k:<12} {v}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: extract_iterm_colors.py <file.itermcolors>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
