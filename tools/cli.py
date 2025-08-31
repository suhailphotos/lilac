#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

# Ensure repo root is importable when running as a script (python tools/cli.py ...)
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from tools.gen import generate_blink_theme
except Exception as e:
    print("error: could not import generate_blink_theme from tools.gen\n"
          f"detail: {e}", file=sys.stderr)
    sys.exit(1)


def main():
    repo_root_default = Path(__file__).resolve().parents[1]  # repo root: $MATRIX/lilac
    template_root_default = Path(__file__).resolve().parent
    p = argparse.ArgumentParser(prog="lilac-cli",
                                description="Lilac toolbox (Blink theme generation)")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("blink", help="Generate Blink theme(s) from palette YAML")
    g = b.add_mutually_exclusive_group(required=True)
    g.add_argument("--yml", nargs="+",
                   help="One or more palette YAMLs (e.g. palettes/lilac-*.yml)")
    g.add_argument("--light",
                   help="Light palette YAML (e.g. palettes/lilac-pearlbloom.yml)")
    b.add_argument("--dark",
                   help="Dark palette YAML (e.g. palettes/lilac-nightbloom.yml)")
    b.add_argument("-o", "--outdir", default="blink/themes",
                   help="Output directory for Blink JS (default: blink/themes)")
    b.add_argument("--template-root", default=str(template_root_default),
                   help="Root containing templates/blink/theme.js.j2 (default: tools)")
    b.add_argument("--cursor-alpha", type=float, default=0.70,
                   help="Cursor RGBA alpha (default: 0.70)")
    b.add_argument("--cursor-blink", action="store_true",
                   help="Enable cursor blinking in Blink")
    b.add_argument("--dry-run", action="store_true",
                   help="Print actions, do not write files")
    b.add_argument("--verbose", "-v", action="store_true",
                   help="Verbose output")

    args = p.parse_args()

    if args.cmd == "blink":
        ymls = []
        if args.yml:
            ymls.extend(args.yml)
        if args.light:
            ymls.append(args.light)
        if args.dark:
            ymls.append(args.dark)

        # De-dup and normalize
        uniq = []
        seen = set()
        for y in ymls:
            pth = str(Path(y))
            if pth not in seen:
                uniq.append(Path(y))
                seen.add(pth)

        if not uniq:
            p.error("no YAML inputs provided")

        outdir = Path(args.outdir)
        jroot = Path(args.template_root)

        for y in uniq:
            name = y.stem + ".js"         # e.g. lilac-nightbloom.yml -> lilac-nightbloom.js
            out_js = outdir / name
            if args.verbose or args.dry_run:
                print(f"[blink] {y} -> {out_js} (template-root={jroot}, "
                      f"alpha={args.cursor_alpha}, blink={args.cursor_blink})")
            if not args.dry_run:
                out_js.parent.mkdir(parents=True, exist_ok=True)
                generate_blink_theme(
                    yaml_path=y,
                    out_js=out_js,
                    jinja_root=jroot,
                    cursor_alpha=args.cursor_alpha,
                    cursor_blink=args.cursor_blink,
                )

if __name__ == "__main__":
    main()
