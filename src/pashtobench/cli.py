"""Command line entry point. I grow the run command into the full runner in sprint 2."""

import argparse

from pashtobench import __version__
from pashtobench.clients import list_specs
from pashtobench.validate import add_validate_parser


def _run_models(args) -> None:
    for spec in list_specs():
        print(
            f"{spec.name:8} {spec.provider:10} {spec.model_id:38} "
            f"in ${spec.price.input_per_m}/M  out ${spec.price.output_per_m}/M"
        )


def add_models_parser(sub) -> None:
    parser = sub.add_parser("models", help="list the configured benchmark models")
    parser.set_defaults(func=_run_models)


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
    add_models_parser(sub)
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
