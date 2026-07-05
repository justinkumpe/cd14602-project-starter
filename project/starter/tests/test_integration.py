"""
Integration tests for the Flashcard Quizzer application flow.
"""

import json

import pytest

from utils.data_loader import load_flashcards
from utils.quiz_engine import QuizEngine
from utils.quiz_modes import SequentialMode


@pytest.fixture
def three_card_deck() -> list[dict[str, str]]:
    """Return a three-card deck for full-session integration tests."""
    return [
        {"front": "HTTP", "back": "Hypertext Transfer Protocol"},
        {"front": "API", "back": "Application Programming Interface"},
        {"front": "DNS", "back": "Domain Name System"},
    ]


def write_deck(tmp_path, deck: list[dict[str, str]]) -> str:
    """Write a flashcard deck to a temporary JSON file."""
    file_path = tmp_path / "deck.json"
    file_path.write_text(json.dumps(deck), encoding="utf-8")
    return str(file_path)


def test_full_session(tmp_path, three_card_deck):
    """Simulate a 3-question session and verify final session statistics."""
    # Arrange
    file_path = write_deck(tmp_path, three_card_deck)
    flashcards = load_flashcards(file_path)
    engine = QuizEngine(flashcards, SequentialMode())
    pending_answers: list[str] = [
        "wrong answer",
        "application programming interface",
        "domain name system",
    ]
    feedback: list[tuple[bool, str]] = []

    def get_answer(card: dict[str, str]) -> str:
        return pending_answers.pop(0)

    def show_feedback(was_correct: bool, card: dict[str, str]) -> None:
        feedback.append((was_correct, card["front"]))

    # Act
    engine.run_quiz(get_answer, show_feedback)
    stats = engine.end_session()

    # Assert
    assert (
        stats["total"] == 3
    ), "Session should record three answered questions"
    assert stats["correct"] == 2, "Two answers should be marked correct"
    assert (
        stats["accuracy_percent"] == 66.67
    ), "Accuracy should reflect two correct answers out of three"
    assert stats["missed_terms"] == [
        "HTTP"
    ], "Missed terms should include fronts answered incorrectly"
    assert feedback == [
        (False, "HTTP"),
        (True, "API"),
        (True, "DNS"),
    ], "Feedback callbacks should reflect answer correctness in order"
