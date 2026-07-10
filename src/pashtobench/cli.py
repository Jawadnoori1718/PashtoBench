"""Command line entry point. I grow this into the full runner in sprint 2."""

import argparse

from pashtobench import __version__


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="pashtobench",
        description="A capability and safety benchmark for Pashto.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"pashtobench {__version__}",
    )
    parser.parse_args(argv)
    # nothing to run yet, so I just show the help for now
    parser.print_help()


if __name__ == "__main__":
    main()
