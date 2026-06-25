#!/usr/bin/env python3

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "typora" / "themes"
DEFAULT_TARGET = (
    Path.home()
    / "Library"
    / "Application Support"
    / "abnerworks.Typora"
    / "themes"
)

THEME_FILES = (
    "lilac-nightbloom.css",
    "lilac-pearlbloom.css",
)


def install_theme(
    source: Path,
    destination: Path,
    *,
    dry_run: bool,
) -> str:
    if not source.is_file():
        raise FileNotFoundError(f"Theme source does not exist: {source}")

    if destination.is_file() and filecmp.cmp(
        source,
        destination,
        shallow=False,
    ):
        return f"unchanged  {destination}"

    if dry_run:
        return f"would copy {source} -> {destination}"

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)

    return f"installed  {destination}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install Lilac themes into Typora on macOS.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET,
        help=f"Typora theme directory (default: {DEFAULT_TARGET})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without copying files.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit unsuccessfully if installed themes differ from the repo.",
    )
    args = parser.parse_args()

    target = args.target.expanduser().resolve()

    if args.check:
        mismatches: list[str] = []

        for filename in THEME_FILES:
            source = SOURCE_DIR / filename
            destination = target / filename

            if not source.is_file():
                mismatches.append(f"missing source: {source}")
            elif not destination.is_file():
                mismatches.append(f"not installed: {destination}")
            elif not filecmp.cmp(source, destination, shallow=False):
                mismatches.append(f"out of date: {destination}")
            else:
                print(f"current    {destination}")

        if mismatches:
            for message in mismatches:
                print(message, file=sys.stderr)
            return 1

        return 0

    for filename in THEME_FILES:
        message = install_theme(
            SOURCE_DIR / filename,
            target / filename,
            dry_run=args.dry_run,
        )
        print(message)

    if not args.dry_run:
        print()
        print("Restart Typora to reload the themes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
