"""
Unit tests for flashcard data loading and validation.
"""

import json
from collections.abc import Callable

import pytest

from utils.data_loader import load_flashcards, main
from utils.exceptions import FlashcardLoadError


@pytest.fixture
def flashcard_file(tmp_path) -> Callable[[str, str], str]:
    """Factory fixture that writes content to a temporary file."""

    def _create(filename: str, content: str) -> str:
        path = tmp_path / filename
        path.write_text(content, encoding="utf-8")
        return str(path)

    return _create


def write_json(
    flashcard_file: Callable[[str, str], str],
    filename: str,
    data: object,
) -> str:
    """Serialize data to JSON and write it to a temporary flashcard file."""
    return flashcard_file(filename, json.dumps(data))


def test_load_valid_flashcards_array(flashcard_file):
    """Array format loads cards with front and back keys."""
    # Arrange
    data = [
        {"front": "HTTP", "back": "Hypertext Transfer Protocol"},
        {"front": "API", "back": "Application Programming Interface"},
    ]
    file_path = write_json(flashcard_file, "array.json", data)

    # Act
    cards = load_flashcards(file_path)

    # Assert
    assert len(cards) == 2, "Expected two flashcards from array format"
    assert cards[0] == {
        "front": "HTTP",
        "back": "Hypertext Transfer Protocol",
    }, "First card should match the source JSON entry"
    assert (
        cards[1]["back"] == "Application Programming Interface"
    ), "Second card back should be preserved"


def test_load_valid_flashcards_wrapper(flashcard_file):
    """Wrapper format with a cards key loads correctly."""
    # Arrange
    data = {
        "cards": [
            {"front": "len()", "back": "Returns the number of items"},
            {"front": "list", "back": "Ordered mutable sequence"},
        ]
    }
    file_path = write_json(flashcard_file, "wrapper.json", data)

    # Act
    cards = load_flashcards(file_path)

    # Assert
    assert len(cards) == 2, "Expected two flashcards from wrapper format"
    assert cards[0]["front"] == "len()", "Wrapper cards should preserve front"
    assert (
        cards[1]["back"] == "Ordered mutable sequence"
    ), "Wrapper cards should preserve back"


def test_load_invalid_json(flashcard_file):
    """Malformed JSON raises FlashcardLoadError with a clear message."""
    # Arrange
    file_path = flashcard_file("broken.json", "{not valid json")

    # Act / Assert
    with pytest.raises(FlashcardLoadError, match="Invalid JSON") as exc_info:
        load_flashcards(file_path)

    assert "broken.json" in str(
        exc_info.value
    ), "Error message should reference the source file"


def test_load_missing_required_field(flashcard_file):
    """Cards missing back raise FlashcardLoadError."""
    # Arrange
    data = [{"front": "Only front provided"}]
    file_path = write_json(flashcard_file, "missing_back.json", data)

    # Act / Assert
    with pytest.raises(
        FlashcardLoadError, match="missing required field 'back'"
    ) as exc_info:
        load_flashcards(file_path)

    assert "Card 1" in str(
        exc_info.value
    ), "Error message should identify the invalid card number"


def test_load_strips_whitespace_from_fields(flashcard_file):
    """Leading and trailing whitespace is stripped from card fields."""
    # Arrange
    data = [{"front": "  DNS  ", "back": "  Domain Name System  "}]
    file_path = write_json(flashcard_file, "whitespace.json", data)

    # Act
    cards = load_flashcards(file_path)

    # Assert
    assert cards[0] == {
        "front": "DNS",
        "back": "Domain Name System",
    }, "Whitespace should be stripped from both fields"


@pytest.mark.parametrize(
    "setup,message",
    [
        pytest.param("missing", "Flashcard file not found", id="missing_file"),
        pytest.param("empty_path", "file path is required", id="empty_path"),
        pytest.param("directory", "is a directory", id="directory_path"),
    ],
)
def test_load_raises_for_file_errors(tmp_path, flashcard_file, setup, message):
    """Missing files and invalid paths raise FlashcardLoadError."""
    # Arrange
    if setup == "missing":
        file_path = str(tmp_path / "does_not_exist.json")
    elif setup == "empty_path":
        file_path = "   "
    else:
        file_path = str(tmp_path)

    # Act / Assert
    with pytest.raises(FlashcardLoadError, match=message):
        load_flashcards(file_path)


@pytest.mark.parametrize(
    "filename,data,message",
    [
        pytest.param(
            "invalid.json",
            {"deck": []},
            "expected a JSON array",
            id="invalid_structure",
        ),
        pytest.param(
            "bad_wrapper.json",
            {"cards": "nope"},
            "'cards' must be a JSON array",
            id="wrapper_cards_not_array",
        ),
        pytest.param(
            "empty_back.json",
            [{"front": "REST", "back": "   "}],
            "field 'back' must be a non-empty string",
            id="empty_required_field",
        ),
        pytest.param(
            "empty_array.json",
            [],
            "contains no cards",
            id="empty_array",
        ),
        pytest.param(
            "empty_wrapper.json",
            {"cards": []},
            "contains no cards",
            id="empty_wrapper",
        ),
        pytest.param(
            "oversized.json",
            None,
            "too large",
            id="oversized_file",
        ),
        pytest.param(
            "non_dict_card.json",
            ["not-an-object"],
            "must be an object",
            id="non_dict_card",
        ),
    ],
)
def test_load_raises_for_invalid_content(
    flashcard_file, filename, data, message
):
    """Invalid structure or card content raises FlashcardLoadError."""
    # Arrange
    if data is None:
        file_path = flashcard_file("oversized.json", "x" * 1_048_577)
    else:
        file_path = write_json(flashcard_file, filename, data)

    # Act / Assert
    with pytest.raises(FlashcardLoadError, match=message):
        load_flashcards(file_path)


@pytest.mark.parametrize(
    "argv,expected_code,expected_output",
    [
        pytest.param([], 1, "Usage:", id="missing_argument"),
        pytest.param(
            ["missing.json"], 1, "Flashcard file not found", id="load_error"
        ),
    ],
)
def test_data_loader_cli_returns_friendly_exit_code(
    capsys, argv, expected_code, expected_output
):
    """Loader CLI should print friendly errors and exit with code 1."""
    # Act
    exit_code = main(argv)
    captured = capsys.readouterr()
    output = captured.err or captured.out

    # Assert
    assert (
        exit_code == expected_code
    ), f"Expected exit code {expected_code}, got {exit_code}"
    assert (
        expected_output in output
    ), f"Expected output to contain '{expected_output}'"


def test_data_loader_cli_reports_success(flashcard_file, capsys):
    """Loader CLI should confirm successful validation with card count."""
    file_path = write_json(
        flashcard_file,
        "valid.json",
        [{"front": "HTTP", "back": "Hypertext Transfer Protocol"}],
    )

    exit_code = main([file_path])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Successfully loaded 1 flashcards." in output


def test_load_raises_for_unreadable_file(tmp_path, monkeypatch):
    """Unreadable files should raise FlashcardLoadError with context."""
    from pathlib import Path

    path = tmp_path / "locked.json"
    path.write_text('[{"front": "Q", "back": "A"}]', encoding="utf-8")
    original_open = Path.open

    def failing_open(self, *args, **kwargs):
        if self == path:
            raise OSError("Permission denied")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", failing_open)

    with pytest.raises(FlashcardLoadError, match="Unable to read"):
        load_flashcards(str(path))
