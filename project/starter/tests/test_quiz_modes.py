"""
Unit tests for quiz mode strategies and the quiz mode factory.
"""

from unittest.mock import patch

import pytest

from utils.quiz_factory import QuizModeFactory
from utils.quiz_modes import AdaptiveMode, RandomMode, SequentialMode


@pytest.fixture
def sample_deck() -> list[dict[str, str]]:
    """Return a small deterministic flashcard deck."""
    return [
        {"front": "Q1", "back": "A1"},
        {"front": "Q2", "back": "A2"},
        {"front": "Q3", "back": "A3"},
    ]


def test_quiz_mode_factory():
    """Factory returns the correct strategy class for each mode string."""
    # Arrange
    cases = [
        ("sequential", SequentialMode),
        ("RANDOM", RandomMode),
        ("Adaptive", AdaptiveMode),
    ]

    # Act / Assert
    for mode_name, expected_class in cases:
        mode = QuizModeFactory.create_mode(mode_name)
        assert isinstance(
            mode, expected_class
        ), f"Expected {expected_class.__name__} for mode '{mode_name}'"

    with pytest.raises(ValueError, match="Unknown quiz mode"):
        QuizModeFactory.create_mode("chaos")


def test_sequential_mode_preserves_order(sample_deck):
    """SequentialMode presents cards in their original order."""
    # Arrange
    mode = SequentialMode()
    state = mode.initialize_state(sample_deck)

    # Act
    order = []
    while True:
        card = mode.next_card(sample_deck, state)
        if card is None:
            break
        order.append(card["front"])

    # Assert
    assert order == [
        "Q1",
        "Q2",
        "Q3",
    ], "Sequential mode should return cards in deck order"
    assert (
        mode.next_card(sample_deck, state) is None
    ), "Sequential mode should return None after the deck is exhausted"


@patch(
    "utils.quiz_modes.random.shuffle",
    side_effect=lambda deck: deck.reverse(),
)
def test_random_mode_produces_permutation(mock_shuffle, sample_deck):
    """RandomMode returns a shuffled permutation of the deck."""
    # Arrange
    mode = RandomMode()
    state = mode.initialize_state(sample_deck)
    mock_shuffle.assert_called_once()

    # Act
    first_pass = [
        mode.next_card(sample_deck, state)["front"] for _ in range(3)
    ]

    # Assert
    assert sorted(first_pass) == [
        "Q1",
        "Q2",
        "Q3",
    ], "Random mode should include every card exactly once per pass"
    assert first_pass == [
        "Q3",
        "Q2",
        "Q1",
    ], "Mocked shuffle should reverse the deck order"


def test_random_mode_empty_deck():
    """RandomMode should return None immediately for an empty deck."""
    mode = RandomMode()
    state = mode.initialize_state([])

    assert mode.next_card([], state) is None


@patch(
    "utils.quiz_modes.random.shuffle",
    side_effect=lambda deck: deck.reverse(),
)
def test_random_mode_reshuffles_when_deck_exhausted(mock_shuffle, sample_deck):
    """RandomMode should reshuffle and continue after a full pass."""
    mode = RandomMode()
    state = mode.initialize_state(sample_deck)
    mock_shuffle.reset_mock()

    for _ in range(3):
        mode.next_card(sample_deck, state)

    fourth = mode.next_card(sample_deck, state)

    assert fourth is not None
    assert mock_shuffle.call_count == 1


def test_adaptive_mode_behavior(sample_deck):
    """AdaptiveMode prioritizes and repeats incorrectly answered cards."""
    # Arrange
    mode = AdaptiveMode()
    state = mode.initialize_state(sample_deck)

    # Act / Assert — first unseen card
    first = mode.next_card(sample_deck, state)
    assert (
        first == sample_deck[0]
    ), "First card should come from remaining deck"

    mode.record_answer(state, first, was_correct=False)
    repeated = mode.next_card(sample_deck, state)
    assert (
        repeated == first
    ), "Incorrect card should be asked again before new cards"

    mode.record_answer(state, repeated, was_correct=True)
    second = mode.next_card(sample_deck, state)
    assert (
        second == sample_deck[1]
    ), "After correcting a card, mode should continue with remaining cards"

    mode.record_answer(state, second, was_correct=False)
    repeated_second = mode.next_card(sample_deck, state)
    assert (
        repeated_second == second
    ), "A newly missed card should also be prioritized"

    mode.record_answer(state, repeated_second, was_correct=True)
    third = mode.next_card(sample_deck, state)
    assert third == sample_deck[2], "Last remaining card should be presented"

    mode.record_answer(state, third, was_correct=True)
    finished = mode.next_card(sample_deck, state)

    assert (
        finished is None
    ), "Adaptive mode should end when every card is answered correctly"
    assert state["wrong_cards"] == [], "No cards should remain in wrong queue"
    assert state["remaining"] == [], "No cards should remain unseen"


def test_adaptive_mode_empty_deck():
    """AdaptiveMode should return None immediately for an empty deck."""
    mode = AdaptiveMode()
    state = mode.initialize_state([])

    assert mode.next_card([], state) is None
