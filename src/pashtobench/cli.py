"""Command line entry point. I grow the run command into the full runner in sprint 2."""

import argparse

from pashtobench import __version__
from pashtobench.clients import list_specs
from pashtobench.leaderboard import build_leaderboard
from pashtobench.runner import add_run_parser
from pashtobench.score import score_translation_run
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


def _run_score(args) -> int:
    payload = score_translation_run(data_dir=args.data_dir, results_dir=args.results_dir)
    print(f"scored {len(payload['scores'])} model and direction cells for {args.task}")
    return 0


def add_score_parser(sub) -> None:
    parser = sub.add_parser("score", help="score cached run outputs for a task")
    parser.add_argument("--task", default="translation", choices=["translation"])
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--results-dir", default="results")
    parser.set_defaults(func=_run_score)


def _run_leaderboard(args) -> int:
    build_leaderboard(results_dir=args.results_dir)
    print(f"wrote {args.results_dir}/leaderboard.md")
    return 0


def add_leaderboard_parser(sub) -> None:
    parser = sub.add_parser("leaderboard", help="render the leaderboard from scores")
    parser.add_argument("--results-dir", default="results")
    parser.set_defaults(func=_run_leaderboard)


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
    add_run_parser(sub)
    add_score_parser(sub)
    add_leaderboard_parser(sub)
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
