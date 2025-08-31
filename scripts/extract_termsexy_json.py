#!/usr/bin/env python3
import sys, json, pathlib

def to_hex(s):
    if not isinstance(s, str):
        return None
    s = s.strip()
    if s.startswith('#') and (len(s) == 7 or len(s) == 4):
        return s.lower()
    return None

def get_palette(obj):
    # Try common shapes:
    # 1) { "palette": { "color0": "#...", ..., "background": "#..." } }
    pal = obj.get("palette") if isinstance(obj, dict) else None
    if pal and isinstance(pal, dict):
        return pal, obj

    # 2) Flat dict with color0..color15 or colors: [...]
    return obj, obj

def get_color_index(pal, idx):
    # list
    if isinstance(pal, list) and len(pal) >= 16:
        return to_hex(pal[idx])
    # dict variants
    keys = [f"color{idx}", f"colour{idx}", str(idx), f"ansi{idx}", f"index{idx}"]
    for k in keys:
        v = pal.get(k) if isinstance(pal, dict) else None
        if v is not None:
            hx = to_hex(v)
            if hx:
                return hx
        # terminal.sexy sometimes nests again: { "colors": { "color0": ... } }
        if isinstance(pal, dict) and "colors" in pal and isinstance(pal["colors"], dict):
            v = pal["colors"].get(k)
            if v is not None:
                hx = to_hex(v)
                if hx:
                    return hx
    # array under 'colors'
    if isinstance(pal, dict) and "colors" in pal and isinstance(pal["colors"], list) and len(pal["colors"]) >= 16:
        return to_hex(pal["colors"][idx])
    return None

def get_simple(pal, obj, name):
    # Try several locations/names
    for src in (pal, obj):
        if isinstance(src, dict):
            for key in (name, name.capitalize(), name.replace('_',' '), name.title() + " Color"):
                v = src.get(key)
                if v:
                    hx = to_hex(v)
                    if hx:
                        return hx
            # nested under 'terminal', 'palette', etc.
            for parent in ("terminal", "palette", "theme"):
                sub = src.get(parent)
                if isinstance(sub, dict):
                    v = sub.get(name) or sub.get(name.capitalize())
                    if v:
                        hx = to_hex(v)
                        if hx:
                            return hx
    return None

def main(path):
    p = pathlib.Path(path)
    data = json.loads(p.read_text())

    pal, root = get_palette(data)

    ansi0 = get_color_index(pal, 0) or "(missing)"
    ansi8 = get_color_index(pal, 8) or "(missing)"
    bg    = get_simple(pal, root, "background")  or "(missing)"
    fg    = get_simple(pal, root, "foreground")  or "(missing)"
    cur   = get_simple(pal, root, "cursor")      or "(missing)"
    curtx = get_simple(pal, root, "cursor_text") or get_simple(pal, root, "cursorText") or "(missing)"

    print(f"file: {path}")
    print(f"{'ansi0':<12}{ansi0}")
    print(f"{'ansi8':<12}{ansi8}")
    print(f"{'background':<12}{bg}")
    print(f"{'foreground':<12}{fg}")
    print(f"{'cursor':<12}{cur}")
    print(f"{'cursor_text':<12}{curtx}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: extract_termsexy_json.py <file.json>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
