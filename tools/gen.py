# tools/gen.py
#!/usr/bin/env python3
import sys, re, plistlib
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

def hex_to_rgb_f(hexstr):
    h = hexstr.lstrip("#")
    return (int(h[0:2],16)/255.0, int(h[2:4],16)/255.0, int(h[4:6],16)/255.0)

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
    """Emit a Lua table (as text) from Python dict/list primitives."""
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

# --------------- load YAML ----------------

def load_common():
    path = PALETTES_DIR / "_common.yml"
    if path.exists():
        data = yaml.safe_load(path.read_text()) or {}
        if not isinstance(data, dict):
            raise ValueError("_common.yml must be a mapping")
        return data
    # Fallback: empty (you can keep behavior purely palette-driven)
    return {}

def load_palettes():
    items = []
    for yml in sorted(PALETTES_DIR.glob("*.yml")):
        if yml.name == "_common.yml":
            continue
        data = yaml.safe_load(yml.read_text())
        pid   = sanitize_id(data["id"])
        label = data.get("label", pid)
        variant = data["variant"]  # catppuccin base: mocha|frappe|...
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
        })
    return items

# --------------- generators ----------------

def gen_lua_core(items):
    # Render lua/lilac/init.lua via Jinja2 template (inject COMMON_HL from _common.yml)
    common = load_common()
    common_highlights = common.get("highlights", {})

    template = env.get_template("lilac_init.lua.j2")
    body = template.render(common_highlights=common_highlights)
    write_text(OUT_NVIM_LUA / "init.lua", body)

    # lua/lilac/flavors.lua (index + list)
    list_tbl = [{"id": it["id"], "label": it["label"], "variant": it["variant"]} for it in items]
    index_tbl = { it["id"]: {
        "variant": it["variant"],
        "cat_overrides": it["cat_overrides"],
        "terminal": it["terminal"],
        "highlights": it["highlights"],
    } for it in items }
    flavors_lua = "return {\n  list = " + lua_table(list_tbl) + ",\n  index = " + lua_table(index_tbl) + "\n}\n"
    write_text(OUT_NVIM_LUA / "flavors.lua", flavors_lua)

def gen_nvim_colors(items):
    # colors/lilac-*.lua → advertise as colorscheme + call module
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
        t = it["tmux"]
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
