"""
CLI smoke-test entry point for flashcard file validation.
"""

import sys

from utils.data_loader import load_flashcards
from utils.exceptions import FlashcardLoadError


def main(argv: list[str] | None = None) -> int:
    """
    Validate a flashcard JSON file from the command line.

    Args:
        argv: Optional command-line arguments. Defaults to ``sys.argv[1:]``.

    Returns:
        Exit code ``0`` on success, ``1`` on load/validation failure.
    """
    args = argv if argv is not None else sys.argv[1:]

    if len(args) != 1:
        print(
            "Usage: python -m utils.data_loader_cli <flashcard.json>",
            file=sys.stderr,
        )
        return 1

    try:
        cards = load_flashcards(args[0])
    except FlashcardLoadError as error:
        print(error, file=sys.stderr)
        return 1

    print(f"Successfully loaded {len(cards)} flashcards.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
