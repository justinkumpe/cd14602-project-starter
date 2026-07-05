"""
Interactive quiz session orchestration.

Coordinates data loading, quiz engine execution, and terminal UI callbacks
without owning CLI argument parsing.
"""

import sys

from utils import ui
from utils.data_loader import load_flashcards
from utils.exceptions import FlashcardLoadError
from utils.quiz_engine import QuizEngine
from utils.quiz_factory import QuizModeFactory
from utils.quiz_modes import Flashcard


def run_quiz_session(
    file_path: str, mode_name: str, show_stats: bool = False
) -> int:
    """
    Load flashcards and run an interactive quiz session.

    Args:
        file_path: Path to the JSON flashcard file.
        mode_name: Quiz mode name accepted by ``QuizModeFactory``.
        show_stats: Whether to print extended session statistics.

    Returns:
        Exit code ``0`` on success, ``1`` on load/setup failure.
    """
    try:
        flashcards = load_flashcards(file_path)
        mode = QuizModeFactory.create_mode(mode_name)
    except FlashcardLoadError as error:
        print(error, file=sys.stderr)
        return 1
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1

    engine = QuizEngine(flashcards, mode)

    def get_answer(card: Flashcard) -> str:
        ui.display_question(card["front"])
        return ui.prompt_answer()

    def show_feedback(was_correct: bool, card: Flashcard) -> None:
        if was_correct:
            ui.display_correct()
        else:
            ui.display_incorrect(card["back"])

    try:
        engine.run_quiz(get_answer, show_feedback)
    except KeyboardInterrupt:
        print("\nSession ended.")

    stats = engine.end_session()
    ui.display_summary(stats)

    if show_stats:
        ui.display_extra_stats(stats, mode_name, len(flashcards))

    return 0
