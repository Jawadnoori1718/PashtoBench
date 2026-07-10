"""Command line entry point. I grow the run command into the full runner in sprint 2."""

import argparse

from pashtobench import __version__
from pashtobench.validate import add_validate_parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pashtobench",
        description="A capability and safety benchmark for Pashto.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"pashtobench {__version__}",
    )
    sub = parser.add_subparsers(dest="command")
    add_validate_parser(sub)
    return parser


def main(argv: list[str] | None = None) -> int | None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return None
    return args.func(args)


if __name__ == "__main__":
    main()
