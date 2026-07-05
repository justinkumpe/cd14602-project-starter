"""
Flashcard Quizzer CLI entry point.

Parses command-line arguments and delegates session execution to
``utils.quiz_session``.
"""

import argparse

from utils.quiz_session import run_quiz_session


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line argument parser.

    Returns:
        Configured ``ArgumentParser`` for the Flashcard Quizzer CLI.
    """
    parser = argparse.ArgumentParser(
        description="Flashcard Quizzer - study with JSON flashcard decks.",
    )
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        help="Path to JSON flashcard file",
    )
    parser.add_argument(
        "-m",
        "--mode",
        default="sequential",
        help=(
            "Quiz mode: sequential, random, or adaptive "
            "(default: sequential)"
        ),
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show extra detail in the session summary",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """
    Parse CLI arguments and run the Flashcard Quizzer.

    Args:
        argv: Optional command-line arguments. Defaults to ``sys.argv[1:]``.

    Returns:
        Process exit code.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_quiz_session(args.file, args.mode, args.stats)


if __name__ == "__main__":
    raise SystemExit(main())
