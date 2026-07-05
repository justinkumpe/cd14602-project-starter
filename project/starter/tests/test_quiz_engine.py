"""
Unit tests for QuizEngine session behavior and edge cases.
"""

import pytest

from utils.quiz_engine import QuizEngine
from utils.quiz_modes import SequentialMode


@pytest.fixture
def sample_deck() -> list[dict[str, str]]:
    """Return a small flashcard deck for engine tests."""
    return [
        {"front": "Q1", "back": "A1"},
        {"front": "Q2", "back": "A2"},
    ]


def test_empty_deck_returns_zero_stats():
    """An empty deck should produce zeroed session statistics."""
    # Arrange
    engine = QuizEngine([], SequentialMode())

    # Act
    engine.run_quiz(lambda card: "answer", lambda ok, card: None)
    stats = engine.end_session()

    # Assert
    assert stats == {
        "total": 0,
        "correct": 0,
        "accuracy_percent": 0.0,
        "missed_terms": [],
    }, "Empty deck sessions should not record any answers"


def test_all_correct_session(sample_deck):
    """All correct answers should produce 100% accuracy and no missed terms."""
    # Arrange
    answers = iter(["a1", "A2"])
    engine = QuizEngine(sample_deck, SequentialMode())

    # Act
    engine.run_quiz(lambda card: next(answers), lambda ok, card: None)
    stats = engine.end_session()

    # Assert
    assert stats["total"] == 2, "Both cards should be counted"
    assert stats["correct"] == 2, "Both answers should be correct"
    assert (
        stats["accuracy_percent"] == 100.0
    ), "Accuracy should be 100% when all answers are correct"
    assert stats["missed_terms"] == [], "No missed terms on a perfect session"


def test_all_wrong_session(sample_deck):
    """All incorrect answers should produce 0% accuracy and missed fronts."""
    # Arrange
    engine = QuizEngine(sample_deck, SequentialMode())

    # Act
    engine.run_quiz(lambda card: "wrong", lambda ok, card: None)
    stats = engine.end_session()

    # Assert
    assert stats["total"] == 2, "Both cards should be counted"
    assert stats["correct"] == 0, "No answers should be correct"
    assert (
        stats["accuracy_percent"] == 0.0
    ), "Accuracy should be 0% when all answers are wrong"
    assert stats["missed_terms"] == [
        "Q1",
        "Q2",
    ], "Every missed front should appear once in missed terms"


def test_exit_mid_quiz_records_partial_stats(sample_deck):
    """Typing exit should end the session and keep partial statistics."""
    # Arrange
    answers = iter(["A1", "exit"])
    engine = QuizEngine(sample_deck, SequentialMode())

    # Act
    engine.run_quiz(lambda card: next(answers), lambda ok, card: None)
    stats = engine.end_session()

    # Assert
    assert stats["total"] == 1, "Only the first answered card should count"
    assert stats["correct"] == 1, "The answered card should be marked correct"
    assert (
        stats["accuracy_percent"] == 100.0
    ), "Partial session accuracy uses only answered questions"
    assert stats["missed_terms"] == [], "No missed terms before exiting"


def test_eof_error_ends_session_with_partial_stats(sample_deck):
    """EOFError from input should end the session without raising."""
    # Arrange
    engine = QuizEngine(sample_deck, SequentialMode())

    def get_answer(card: dict[str, str]) -> str:
        if card["front"] == "Q1":
            return "A1"
        raise EOFError

    # Act
    engine.run_quiz(get_answer, lambda ok, card: None)
    stats = engine.end_session()

    # Assert
    assert stats["total"] == 1, "Only answers before EOF should be counted"
    assert stats["correct"] == 1, "Valid answer before EOF should be recorded"
