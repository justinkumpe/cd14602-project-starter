"""
Flashcard data loading and validation from JSON files.

This module handles parsing two supported JSON formats and ensures every
card contains non-empty string values for ``front`` and ``back``.
"""

import json
from pathlib import Path
from typing import Any

from utils.exceptions import FlashcardLoadError

_REQUIRED_FIELDS = ("front", "back")
_MAX_FLASHCARD_FILE_BYTES = 1_048_576  # 1 MB


def load_flashcards(file_path: str) -> list[dict[str, str]]:
    """
    Load and validate flashcards from a JSON file.

    Supports two JSON formats:

    1. Array: ``[{"front": "...", "back": "..."}, ...]``
    2. Wrapper: ``{"cards": [{"front": "...", "back": "..."}, ...]}``

    Args:
        file_path: Path to the JSON flashcard file.

    Returns:
        A list of validated flashcard dictionaries with ``front`` and
        ``back`` keys.

    Raises:
        FlashcardLoadError: If the path is invalid, the file is missing,
            contains invalid JSON, has no cards, or has cards with missing
            or invalid ``front``/``back`` values.
    """
    if not file_path or not file_path.strip():
        raise FlashcardLoadError("A flashcard file path is required.")

    path = Path(file_path)
    data = _load_json(path)
    raw_cards = _extract_cards(data, path)

    if not raw_cards:
        raise FlashcardLoadError(f"Flashcard file '{path}' contains no cards.")

    return _validate_cards(raw_cards)


def _load_json(path: Path) -> Any:
    """
    Read and parse JSON from the given file path.

    Args:
        path: Path to the JSON file.

    Returns:
        The parsed JSON value.

    Raises:
        FlashcardLoadError: If the file does not exist or JSON is malformed.
    """
    if path.is_dir():
        raise FlashcardLoadError(
            f"Flashcard path is a directory, not a file: {path}"
        )
    if not path.is_file():
        raise FlashcardLoadError(f"Flashcard file not found: {path}")

    file_size = path.stat().st_size
    if file_size > _MAX_FLASHCARD_FILE_BYTES:
        raise FlashcardLoadError(
            f"Flashcard file '{path}' is too large ({file_size} bytes). "
            f"Maximum allowed size is {_MAX_FLASHCARD_FILE_BYTES} bytes."
        )

    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as error:
        raise FlashcardLoadError(
            f"Invalid JSON in flashcard file '{path}' "
            f"(line {error.lineno}, column {error.colno}): {error.msg}. "
            "Please check the file format and try again."
        ) from None
    except OSError as error:
        raise FlashcardLoadError(
            f"Unable to read flashcard file '{path}': {error}"
        ) from None


def _extract_cards(data: Any, path: Path) -> list[Any]:
    """
    Extract the card list from supported top-level JSON structures.

    Args:
        data: Parsed JSON content.
        path: Source file path, used in error messages.

    Returns:
        The raw list of card objects before field validation.

    Raises:
        FlashcardLoadError: If the JSON structure is not a supported format.
    """
    if isinstance(data, list):
        return data

    if isinstance(data, dict) and "cards" in data:
        cards = data["cards"]
        if not isinstance(cards, list):
            raise FlashcardLoadError(
                f"Invalid flashcard file '{path}': "
                "'cards' must be a JSON array."
            )
        return cards

    raise FlashcardLoadError(
        f"Invalid flashcard file '{path}': "
        "expected a JSON array or an object with a 'cards' array."
    )


def _validate_cards(raw_cards: list[Any]) -> list[dict[str, str]]:
    """
    Validate that every card has non-empty string ``front`` and ``back``
    fields.

    Args:
        raw_cards: Card objects loaded from JSON.

    Returns:
        A list of validated flashcard dictionaries.

    Raises:
        FlashcardLoadError: If any card is missing required fields or has
            invalid values.
    """
    validated_cards: list[dict[str, str]] = []

    for index, card in enumerate(raw_cards, start=1):
        if not isinstance(card, dict):
            raise FlashcardLoadError(
                f"Card {index} must be an object with "
                "'front' and 'back' fields."
            )

        validated_card: dict[str, str] = {}
        for field in _REQUIRED_FIELDS:
            if field not in card:
                raise FlashcardLoadError(
                    f"Card {index} is missing required field '{field}'."
                )

            value = card[field]
            if not isinstance(value, str) or not value.strip():
                raise FlashcardLoadError(
                    f"Card {index} field '{field}' must be a non-empty string."
                )

            validated_card[field] = value.strip()

        validated_cards.append(validated_card)

    return validated_cards


from utils.data_loader_cli import main  # noqa: E402,F401
