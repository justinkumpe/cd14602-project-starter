"""
Quiz mode strategies for the Flashcard Quizzer.

This module applies the Strategy Pattern so the quiz engine can swap card
selection algorithms (sequential, random, adaptive) at runtime without
changing its core loop.
"""

import random
from abc import ABC, abstractmethod
from typing import Any

Flashcard = dict[str, str]
SessionState = dict[str, Any]


class QuizMode(ABC):
    """Abstract strategy for selecting the next flashcard in a session."""

    @abstractmethod
    def initialize_state(self, deck: list[Flashcard]) -> SessionState:
        """
        Create the initial session state for a quiz mode.

        Args:
            deck: The full list of flashcards for the session.

        Returns:
            A mutable state dictionary used across ``next_card`` calls.
        """

    @abstractmethod
    def next_card(
        self, deck: list[Flashcard], state: SessionState
    ) -> Flashcard | None:
        """
        Select the next flashcard to present.

        Args:
            deck: The full list of flashcards for the session.
            state: Mutable session state for this quiz mode.

        Returns:
            The next flashcard dictionary, or ``None`` when the mode has no
            more cards to present under its completion rules.
        """

    def record_answer(
        self,
        state: SessionState,
        card: Flashcard,
        was_correct: bool,
    ) -> None:
        """
        Update session state after the user answers a card.

        Args:
            state: Mutable session state for this quiz mode.
            card: The flashcard that was just answered.
            was_correct: Whether the user's answer was correct.
        """
        results = state.setdefault("results", [])
        results.append({"card": card, "was_correct": was_correct})


class SequentialMode(QuizMode):
    """Present cards in their original order from first to last."""

    def initialize_state(self, deck: list[Flashcard]) -> SessionState:
        """Initialize index tracking for sequential traversal."""
        return {"index": 0, "results": []}

    def next_card(
        self, deck: list[Flashcard], state: SessionState
    ) -> Flashcard | None:
        """Return the next card in order until the deck is exhausted."""
        if not deck:
            return None

        index = state["index"]
        if index >= len(deck):
            return None

        card = deck[index]
        state["index"] = index + 1
        return card


class RandomMode(QuizMode):
    """
    Present cards in a shuffled order.

    When every card in the current shuffle has been shown, the deck is
    reshuffled and the session continues. An empty deck yields ``None``.
    """

    def initialize_state(self, deck: list[Flashcard]) -> SessionState:
        """Initialize a shuffled working deck and position index."""
        shuffled_deck = deck.copy()
        random.shuffle(shuffled_deck)
        return {
            "shuffled_deck": shuffled_deck,
            "index": 0,
            "results": [],
        }

    def next_card(
        self, deck: list[Flashcard], state: SessionState
    ) -> Flashcard | None:
        """Return the next shuffled card, reshuffling when exhausted."""
        if not deck:
            return None

        if state["index"] >= len(state["shuffled_deck"]):
            state["shuffled_deck"] = deck.copy()
            random.shuffle(state["shuffled_deck"])
            state["index"] = 0

        shuffled_deck: list[Flashcard] = state["shuffled_deck"]
        card = shuffled_deck[state["index"]]
        state["index"] += 1
        return card


class AdaptiveMode(QuizMode):
    """
    Prioritize cards the user previously answered incorrectly.

    Algorithm:
    1. ``next_card`` serves cards from ``wrong_cards`` first (FIFO), then
       unseen cards from ``remaining``.
    2. On a wrong answer, ``record_answer`` appends the card to
       ``wrong_cards`` so it is asked again before new cards.
    3. On a correct answer, the card is not re-queued.
    4. The session ends when both queues are empty (all cards mastered).
    """

    def initialize_state(self, deck: list[Flashcard]) -> SessionState:
        """Initialize queues for unseen and incorrectly answered cards."""
        return {
            "remaining": deck.copy(),
            "wrong_cards": [],
            "results": [],
        }

    def next_card(
        self, deck: list[Flashcard], state: SessionState
    ) -> Flashcard | None:
        """Return the next prioritized card or None when all are correct."""
        if not deck:
            return None

        # Wrong cards take priority over unseen cards.
        if state["wrong_cards"]:
            wrong_cards: list[Flashcard] = state["wrong_cards"]
            return wrong_cards.pop(0)
        if state["remaining"]:
            remaining: list[Flashcard] = state["remaining"]
            return remaining.pop(0)
        return None

    def record_answer(
        self,
        state: SessionState,
        card: Flashcard,
        was_correct: bool,
    ) -> None:
        """
        Re-queue incorrect cards until they are answered correctly.

        Args:
            state: Mutable session state for this quiz mode.
            card: The flashcard that was just answered.
            was_correct: Whether the user's answer was correct.
        """
        super().record_answer(state, card, was_correct)

        if was_correct:
            return

        # Append only if not already queued (e.g. double-record guard).
        if card not in state["wrong_cards"]:
            state["wrong_cards"].append(card)
