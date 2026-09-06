"""githood — one spec in, one repo out."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import receipts, scaffold
from .spec import SpecError, load

VERSION = "0.1.0"

BANNER = r"""
  ___ ___ _____ _  _  ___  ___  ___
 / __|_ _|_   _| || |/ _ \/ _ \|   \
| (_ || |  | | | __ | (_) | (_) | |) |
 \___|___| |_| |_||_|\___/ \___/|___/   one spec in, one repo out
"""


def cmd_plan(args) -> int:
    spec = load(args.spec)
    print(BANNER.strip("\n"))
    print(f"\n  {spec.summary()}\n")
    for rel in scaffold.plan(spec):
        print(f"    {rel}")
    print(f"\n  {len(scaffold.plan(spec))} files, nothing written (this is a plan)")
    return 0


def cmd_new(args) -> int:
    spec = load(args.spec)
    out = Path(args.out or spec.slug)
    if args.dry_run:
        print(f"would write {len(scaffold.plan(spec))} files into {out}/")
        return 0

    result = scaffold.build(
        spec, out, spec_file=str(args.spec), force=args.force, git=not args.no_git
    )
    receipt = receipts.write(result, spec, str(args.spec))

    print(f"{spec.name} -> {result.root}/")
    print(f"  {result.summary}")
    print(f"  receipt: {receipt.relative_to(result.root)}")
    print("\nnext:")
    print(f"  cd {result.root} && cp .env.example .env && make test")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="githood", description=__doc__)
    p.add_argument("--version", action="version", version=f"githood {VERSION}")
    sub = p.add_subparsers(dest="cmd", required=True)

    new = sub.add_parser("new", help="write the repo")
    new.add_argument("spec", help="path to the spec file")
    new.add_argument("-o", "--out", help="output directory (default: the spec slug)")
    new.add_argument("--force", action="store_true", help="overwrite a non-empty directory")
    new.add_argument("--no-git", action="store_true", help="skip git init and the first commit")
    new.add_argument("--dry-run", action="store_true", help="say what would happen, write nothing")
    new.set_defaults(func=cmd_new)

    plan = sub.add_parser("plan", help="print the tree without writing it")
    plan.add_argument("spec", help="path to the spec file")
    plan.set_defaults(func=cmd_plan)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except SpecError as exc:
        print(f"spec error: {exc}", file=sys.stderr)
        return 2
    except FileExistsError as exc:
        print(f"{exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
