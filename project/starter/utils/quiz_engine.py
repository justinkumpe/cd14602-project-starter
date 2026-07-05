"""
Quiz engine for running flashcard sessions.

The engine coordinates a ``QuizMode`` strategy with caller-provided callbacks
so presentation and input stay outside this module (for example, in ``ui.py``).
"""

from collections.abc import Callable
from typing import Any

from utils.quiz_modes import Flashcard, QuizMode, SessionState

GetAnswerCallback = Callable[[Flashcard], str]
ShowFeedbackCallback = Callable[[bool, Flashcard], None]
SessionStats = dict[str, Any]


class QuizEngine:
    """Run a flashcard quiz session using a pluggable quiz mode strategy."""

    def __init__(self, flashcards: list[Flashcard], mode: QuizMode) -> None:
        """
        Initialize a quiz session.

        Args:
            flashcards: The deck of flashcards to quiz.
            mode: The strategy that determines card selection order.
        """
        self._deck = flashcards
        self._mode = mode
        self._state: SessionState = mode.initialize_state(flashcards)
        self._total = 0
        self._correct = 0
        self._missed_terms: list[str] = []

    def run_quiz(
        self,
        get_answer: GetAnswerCallback,
        show_feedback: ShowFeedbackCallback,
    ) -> None:
        """
        Run the quiz loop until the mode is exhausted or the user exits.

        The engine delegates all user interaction to callbacks so it never
        prints to the terminal directly.

        Args:
            get_answer: Callable that presents a card and returns the user's
                answer. Returning ``"exit"`` (case-insensitive) or raising
                ``EOFError`` (for example, Ctrl+D) ends the session early.
            show_feedback: Callable that displays whether the answer was
                correct for the given card.
        """
        while True:
            card = self._mode.next_card(self._deck, self._state)
            if card is None:
                break

            try:
                answer = get_answer(card)
            except EOFError:
                break

            if answer.strip().lower() == "exit":
                break

            was_correct = self._is_correct(answer, card)
            self._record_result(card, was_correct)
            self._mode.record_answer(self._state, card, was_correct)
            show_feedback(was_correct, card)

    def end_session(self) -> SessionStats:
        """
        Return per-session statistics for the completed quiz.

        Returns:
            A dictionary containing ``total``, ``correct``,
            ``accuracy_percent``, and ``missed_terms``.
        """
        return {
            "total": self._total,
            "correct": self._correct,
            "accuracy_percent": self._calculate_accuracy_percent(),
            "missed_terms": self._missed_terms.copy(),
        }

    @staticmethod
    def _is_correct(user_answer: str, card: Flashcard) -> bool:
        """
        Compare a user answer to the card back case-insensitively.

        Args:
            user_answer: The answer provided by the user.
            card: The flashcard being evaluated.

        Returns:
            ``True`` if the normalized answers match, otherwise ``False``.
        """
        return (
            user_answer.strip().casefold() == card["back"].strip().casefold()
        )

    def _record_result(self, card: Flashcard, was_correct: bool) -> None:
        """
        Update session statistics after a single answer.

        Args:
            card: The flashcard that was answered.
            was_correct: Whether the user's answer was correct.
        """
        self._total += 1
        if was_correct:
            self._correct += 1
        elif card["front"] not in self._missed_terms:
            self._missed_terms.append(card["front"])

    def _calculate_accuracy_percent(self) -> float:
        """Calculate session accuracy as a percentage."""
        if self._total == 0:
            return 0.0
        return round((self._correct / self._total) * 100, 2)
