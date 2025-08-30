# tools/gen.py
#!/usr/bin/env python3
import sys, re, plistlib, math
from pathlib import Path

try:
    import yaml
except Exception:
    print("This tool needs PyYAML. Install: pip install pyyaml", file=sys.stderr)
    raise

try:
    from jinja2 import Environment, FileSystemLoader
except Exception:
    print("This tool needs Jinja2. Install: pip install jinja2", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[1]
PALETTES_DIR = ROOT / "palettes"
TEMPLATES_DIR = ROOT / "tools" / "templates"

OUT_NVIM_COLORS = ROOT / "colors"
OUT_NVIM_LUA = ROOT / "lua" / "lilac"
OUT_GHOSTTY = ROOT / "ghostty" / "themes"
OUT_TMUX = ROOT / "tmux"
OUT_ITERM = ROOT / "iterm"

for p in (OUT_NVIM_COLORS, OUT_NVIM_LUA, OUT_GHOSTTY, OUT_TMUX, OUT_ITERM, TEMPLATES_DIR):
    p.mkdir(parents=True, exist_ok=True)

# ---------------- helpers ----------------

HEX_RE = re.compile(r'^#?[0-9A-Fa-f]{6}$')
ANSI_RE = re.compile(r'^@(?:ansi|term)\[(\d{1,2})\]$')
SIMPLE_TOKEN_RE = re.compile(r'^@(fg|bg|cursor|cursor_text|sel_bg|sel_fg)$')
BLEND_RE = re.compile(r'^blend\((.+?),\s*(.+?),\s*([01](?:\.\d+)?)\)$')

def hex_to_rgb_f(hexstr):
    h = hexstr.strip().lstrip("#")
    if len(h) != 6:
        raise ValueError(f"Bad hex: {hexstr}")
    return (int(h[0:2],16)/255.0, int(h[2:4],16)/255.0, int(h[4:6],16)/255.0)

def rgb_to_hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(
        max(0,min(255, round(r*255))),
        max(0,min(255, round(g*255))),
        max(0,min(255, round(b*255))),
    )

def write_text(path: Path, s: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(s, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))

def sanitize_id(x: str) -> str:
    x = x.strip().lower()
    if not x.startswith("lilac-"):
        x = "lilac-" + x
    return re.sub(r"[^a-z0-9\-]", "-", x)

def lua_table(obj, indent=0):
    sp = "  " * indent
    if isinstance(obj, dict):
        rows = []
        for k, v in obj.items():
            key = f'["{k}"]'
            rows.append(sp + "  " + f"{key} = " + lua_table(v, indent+1))
        return "{\n" + ",\n".join(rows) + "\n" + sp + "}"
    if isinstance(obj, list):
        rows = [sp + "  " + lua_table(v, indent+1) for v in obj]
        return "{\n" + ",\n".join(rows) + "\n" + sp + "}"
    if isinstance(obj, str):
        return '"' + obj.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if obj is True:  return "true"
    if obj is False: return "false"
    if obj is None:  return "nil"
    return str(obj)

# Jinja2 env with `luadump` filter
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), trim_blocks=True, lstrip_blocks=True)
env.filters["luadump"] = lambda obj: lua_table(obj, 0)

# --------------- variable resolver ----------------

def _read_term_entry(term: dict, idx: int) -> str:
    colors = term.get("colors") or []
    if idx < 0 or idx >= len(colors):
        raise ValueError(f"@ansi[{idx}] out of range")
    return colors[idx]

def _read_simple_token(term: dict, name: str) -> str:
    m = {
        "fg": term.get("foreground"),
        "bg": term.get("background"),
        "cursor": term.get("cursor") or term.get("foreground"),
        "cursor_text": term.get("cursor_text") or term.get("background"),
        "sel_bg": term.get("selection_background"),
        "sel_fg": term.get("selection_foreground"),
    }[name]
    if not m:
        # pick a sane fallback
        if name in ("fg","cursor"): return term.get("foreground") or "#ffffff"
        if name in ("bg","cursor_text"): return term.get("background") or "#000000"
        return term.get("foreground") or "#ffffff"
    return m

def _eval_color_atom(s: str, term: dict) -> str:
    s = s.strip()
    if s.startswith("@C.") or s == "@comment":
        # Leave runtime-resolved tokens for Lua
        return s
    if HEX_RE.match(s):
        return "#" + s.lstrip("#").lower()
    m = ANSI_RE.match(s)
    if m:
        return _read_term_entry(term, int(m.group(1))).lower()
    m = SIMPLE_TOKEN_RE.match(s)
    if m:
        return _read_simple_token(term, m.group(1)).lower()
    # Not a direct atom → maybe it's an expression; handled by caller
    return s

def _eval_expr(expr: str, term: dict) -> str:
    expr = expr.strip()
    # blend(A,B,t)
    m = BLEND_RE.match(expr)
    if m:
        a = _eval_color_atom(m.group(1), term)
        b = _eval_color_atom(m.group(2), term)
        t = float(m.group(3))
        if a.startswith("@C.") or b.startswith("@C.") or a == "@comment" or b == "@comment":
            # Can't blend runtime tokens; just return A for safety
            return a
        ra,ga,ba = hex_to_rgb_f(a)
        rb,gb,bb = hex_to_rgb_f(b)
        r = (1.0 - t)*ra + t*rb
        g = (1.0 - t)*ga + t*gb
        b = (1.0 - t)*ba + t*bb
        return rgb_to_hex(r,g,b)
    # fall back to atom
    atom = _eval_color_atom(expr, term)
    if atom.startswith("@C.") or atom == "@comment":
        return atom
    return atom

def resolve_palette_value(v, term: dict):
    if isinstance(v, str):
        # Keep @C.* and @comment for runtime; resolve everything else
        if v.startswith("@C.") or v == "@comment":
            return v
        return _eval_expr(v, term)
    if isinstance(v, list):
        return [resolve_palette_value(x, term) for x in v]
    if isinstance(v, dict):
        return {k: resolve_palette_value(x, term) for k, x in v.items()}
    return v

def resolve_mapping(m: dict, term: dict) -> dict:
    if not isinstance(m, dict): return {}
    out = {}
    for k, v in m.items():
        out[k] = resolve_palette_value(v, term)
    return out

# --------------- load YAML ----------------

def load_common():
    path = PALETTES_DIR / "_common.yml"
    if path.exists():
        data = yaml.safe_load(path.read_text()) or {}
        if not isinstance(data, dict):
            raise ValueError("_common.yml must be a mapping")
        return data
    return {}

def load_palettes():
    items = []
    for yml in sorted(PALETTES_DIR.glob("*.yml")):
        if yml.name == "_common.yml":
            continue
        data = yaml.safe_load(yml.read_text())
        pid   = sanitize_id(data["id"])
        label = data.get("label", pid)
        variant = data["variant"]
        term = data["terminal"]
        colors16 = term["colors"]
        if len(colors16) != 16:
            raise ValueError(f"{pid}: terminal.colors must have 16 entries")
        items.append({
            "id": pid,
            "label": label,
            "variant": variant,
            "terminal": term,
            "cat_overrides": data.get("catppuccin_overrides", {}),
            "highlights": data.get("highlights", {}),
            "tmux": data.get("tmux", {}),
            "comment": data.get("comment"),
        })
    return items

# --------------- generators ----------------

def gen_lua_core(items):
    common = load_common()
    common_highlights = common.get("highlights", {})

    template = env.get_template("lilac_init.lua.j2")
    body = template.render(common_highlights=common_highlights)
    write_text(OUT_NVIM_LUA / "init.lua", body)

    index_tbl = {}
    list_tbl = []
    for it in items:
        pid = it["id"]
        list_tbl.append({"id": pid, "label": it["label"], "variant": it["variant"]})

        term = it["terminal"]

        # NEW: resolve comment so @ansi[...] / blend(...) become hex here
        resolved_comment = None
        if it.get("comment") is not None:
            resolved_comment = resolve_palette_value(it.get("comment"), term)

        overrides = resolve_mapping(it["cat_overrides"], term)
        tmux_map  = resolve_mapping(it["tmux"], term)

        # Resolve @ansi/@fg/... in palette-specific highlights; keep @C.* and @comment for runtime
        highlights = {}
        for k, v in (it["highlights"] or {}).items():
            highlights[k] = resolve_palette_value(v, term)

        index_tbl[pid] = {
            "variant": it["variant"],
            "cat_overrides": overrides,
            "terminal": term,
            "highlights": highlights,
            "comment": resolved_comment,  # <-- use resolved value
            "tmux": tmux_map,
        }

    flavors_lua = "return {\n  list = " + lua_table(list_tbl) + ",\n  index = " + lua_table(index_tbl) + "\n}\n"
    write_text(OUT_NVIM_LUA / "flavors.lua", flavors_lua)

def gen_nvim_colors(items):
    for it in items:
        s = f'vim.g.colors_name = "{it["id"]}"\nrequire("lilac").load("{it["id"]}")\n'
        write_text(OUT_NVIM_COLORS / (it["id"] + ".lua"), s)

def gen_ghostty(items):
    for it in items:
        term = it["terminal"]
        lines = []
        for i, hx in enumerate(term["colors"]):
            lines.append(f"palette = {i}={hx}")
        mapkeys = {
          "background": "background",
          "foreground": "foreground",
          "cursor": "cursor-color",
          "cursor_text": "cursor-text",
          "selection_background": "selection-background",
          "selection_foreground": "selection-foreground",
        }
        for k, outk in mapkeys.items():
            v = term.get(k)
            if v: lines.append(f"{outk} = {v}")
        write_text(OUT_GHOSTTY / it["id"], "\n".join(lines) + "\n")

def gen_iterm(items):
    for it in items:
        term = it["terminal"]
        d = {}
        for i, hx in enumerate(term["colors"]):
            r,g,b = hex_to_rgb_f(hx)
            d[f"Ansi {i} Color"] = { "Red Component": r, "Green Component": g, "Blue Component": b }
        extra = {
          "Foreground Color": term.get("foreground"),
          "Background Color": term.get("background"),
          "Cursor Color": term.get("cursor"),
          "Cursor Text Color": term.get("cursor_text"),
          "Selection Color": term.get("selection_background"),
          "Selected Text Color": term.get("selection_foreground"),
        }
        for k, hexv in extra.items():
            if not hexv: continue
            r,g,b = hex_to_rgb_f(hexv)
            d[k] = { "Red Component": r, "Green Component": g, "Blue Component": b }
        out = OUT_ITERM / f'{it["id"]}.itermcolors'
        with open(out, "wb") as f:
            plistlib.dump(d, f)
        print("wrote", out.relative_to(ROOT))

def gen_tmux(items):
    parts = [
        "# lilac/tmux: set @lilac_flavor to one of the generated flavors, then reload tmux",
        'set -gq @lilac_flavor "#{@@lilac_flavor}"',
        'if -b \'[ -z "#{@@lilac_flavor}" ]\' { set -g @lilac_flavor "nightbloom" }',
    ]
    for it in items:
        flavor = it["id"].split("lilac-")[-1]
        t = resolve_mapping(it.get("tmux", {}), it["terminal"])
        status_fg = t.get("status_fg", "#7c87a8")
        status_bg = t.get("status_bg", "#1a1b25")
        msg_fg    = t.get("message_fg", "#cfd6f5")
        msg_bg    = t.get("message_bg", "#4c4e69")
        pb        = t.get("pane_border", "#4c4e69")
        pab       = t.get("pane_active_border", "#87abf5")
        parts += [
            f'if -b \'[ "#{{@@lilac_flavor}}" = "{flavor}" ]\' {{',
            f'  set -g status-style "fg={status_fg},bg={status_bg}"',
            f'  set -g message-style "fg={msg_fg},bg={msg_bg}"',
            f'  set -g pane-border-style "fg={pb}"',
            f'  set -g pane-active-border-style "fg={pab}"',
            '  set -g status-left ""',
            f'  set -g status-right "#[fg={pab}]#S #[fg={status_fg}]| %H:%M"',
            f'}}'
        ]
    write_text(OUT_TMUX / "lilac.tmux", "\n".join(parts) + "\n")

def main():
    items = load_palettes()
    if not items:
        print("No palettes found in palettes/*.yml", file=sys.stderr); sys.exit(1)
    gen_lua_core(items)
    gen_nvim_colors(items)
    gen_ghostty(items)
    gen_iterm(items)
    gen_tmux(items)
    print("Done. Palettes:", ", ".join([i["id"] for i in items]))

if __name__ == "__main__":
    main()
