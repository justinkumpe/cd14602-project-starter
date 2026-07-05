"""
Terminal UI helpers for the Flashcard Quizzer.

Formatting helpers are kept pure for easy testing; display functions are thin
wrappers that write formatted output to the terminal.
"""

import os
import sys
from typing import Any, TextIO

GREEN = "\033[32m"
RED = "\033[31m"
BOLD = "\033[1m"
RESET = "\033[0m"

_DEFAULT_PROMPT = "Your answer (or 'exit' to quit): "


def supports_color(stream: TextIO | None = None) -> bool:
    """
    Determine whether ANSI color codes should be used.

    Args:
        stream: Output stream to inspect. Defaults to ``sys.stdout``.

    Returns:
        ``True`` when the stream likely supports color output.
    """
    if os.environ.get("NO_COLOR") is not None:
        return False

    output = stream or sys.stdout
    term = os.environ.get("TERM", "")
    return output.isatty() and term.lower() not in {"", "dumb"}


def colorize(text: str, ansi_code: str, *, use_color: bool = True) -> str:
    """
    Wrap text in ANSI color codes when color output is enabled.

    Args:
        text: Text to colorize.
        ansi_code: ANSI escape sequence for the desired color/style.
        use_color: Whether to apply color formatting.

    Returns:
        The original text or a colorized version.
    """
    if not use_color:
        return text
    return f"{ansi_code}{text}{RESET}"


def format_question(front: str) -> str:
    """
    Format a flashcard question for display.

    Args:
        front: The prompt shown to the user.

    Returns:
        A formatted question string.
    """
    use_color = supports_color()
    label = colorize("Question:", BOLD, use_color=use_color)
    return f"\n{label} {front}"


def format_correct(*, use_color: bool | None = None) -> str:
    """
    Format a correct-answer feedback message.

    Args:
        use_color: Force color on/off. Auto-detects when ``None``.

    Returns:
        A formatted feedback string.
    """
    if use_color is None:
        use_color = supports_color()
    return colorize("Correct!", GREEN, use_color=use_color)


def format_incorrect(
    correct_answer: str, *, use_color: bool | None = None
) -> str:
    """
    Format an incorrect-answer feedback message.

    Args:
        correct_answer: The expected answer for the card.
        use_color: Force color on/off. Auto-detects when ``None``.

    Returns:
        A formatted feedback string.
    """
    if use_color is None:
        use_color = supports_color()
    message = f"Incorrect. Correct answer: {correct_answer}"
    return colorize(message, RED, use_color=use_color)


def format_summary(stats: dict[str, Any]) -> str:
    """
    Format session statistics as a readable summary table.

    Args:
        stats: Session stats with ``total``, ``accuracy_percent``, and
            ``missed_terms`` keys.

    Returns:
        A multi-line summary string.
    """
    total = stats.get("total", 0)
    accuracy = stats.get("accuracy_percent", 0.0)
    missed_terms = stats.get("missed_terms", [])

    label_width = 18
    lines = [
        "",
        colorize("Session Summary", BOLD, use_color=supports_color()),
        "=" * 32,
        f"{'Total Questions':<{label_width}} {total}",
        f"{'Accuracy %':<{label_width}} {accuracy}",
        "-" * 32,
    ]

    if missed_terms:
        lines.append("Missed terms:")
        lines.extend(f"  - {term}" for term in missed_terms)
    else:
        lines.append("Missed terms: none")

    return "\n".join(lines)


def display_question(front: str) -> None:
    """
    Display a flashcard question in the terminal.

    Args:
        front: The prompt shown to the user.
    """
    print(format_question(front))


def display_correct() -> None:
    """Display positive feedback for a correct answer."""
    print(format_correct())


def display_incorrect(correct_answer: str) -> None:
    """
    Display feedback for an incorrect answer.

    Args:
        correct_answer: The expected answer for the card.
    """
    print(format_incorrect(correct_answer))


def display_summary(stats: dict[str, Any]) -> None:
    """
    Display the end-of-session statistics table.

    Args:
        stats: Session stats with ``total``, ``accuracy_percent``, and
            ``missed_terms`` keys.
    """
    print(format_summary(stats))


def display_extra_stats(
    stats: dict[str, Any], mode_name: str, deck_size: int
) -> None:
    """
    Display optional extended session statistics.

    Args:
        stats: Session statistics from ``QuizEngine.end_session``.
        mode_name: The quiz mode used for the session.
        deck_size: Number of flashcards in the loaded deck.
    """
    correct = int(stats.get("correct", 0))
    total = int(stats.get("total", 0))
    print(f"Correct answers:   {correct}")
    print(f"Incorrect answers: {total - correct}")
    print(f"Quiz mode:         {mode_name}")
    print(f"Deck size:         {deck_size}")


def prompt_answer(prompt: str = _DEFAULT_PROMPT) -> str:
    """
    Prompt the user for an answer.

    Args:
        prompt: Prompt text shown before reading input.

    Returns:
        The user's answer, stripped of leading and trailing whitespace.
    """
    return input(prompt).strip()
