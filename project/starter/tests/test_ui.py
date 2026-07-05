"""
Unit tests for terminal UI formatting and interaction helpers.
"""

from utils.ui import (
    GREEN,
    colorize,
    display_correct,
    display_extra_stats,
    display_incorrect,
    display_question,
    display_summary,
    format_correct,
    format_incorrect,
    format_summary,
    prompt_answer,
    supports_color,
)


def test_format_summary_with_missed_terms():
    """Summary should list missed term fronts when present."""
    # Arrange
    stats = {
        "total": 2,
        "accuracy_percent": 50.0,
        "missed_terms": ["HTTP"],
    }

    # Act
    summary = format_summary(stats)

    # Assert
    assert (
        "Total Questions" in summary
    ), "Summary should include total questions"
    assert "Accuracy %" in summary, "Summary should include accuracy"
    assert (
        "Missed terms:" in summary
    ), "Summary should include missed terms header"
    assert "HTTP" in summary, "Missed front should appear in summary"


def test_format_summary_without_missed_terms():
    """Summary should report none when every answer was correct."""
    # Arrange
    stats = {
        "total": 2,
        "accuracy_percent": 100.0,
        "missed_terms": [],
    }

    # Act
    summary = format_summary(stats)

    # Assert
    assert (
        "Missed terms: none" in summary
    ), "Summary should state when there are no missed terms"


def test_colorize_respects_use_color_flag():
    """Colorize should skip ANSI codes when color output is disabled."""
    # Act / Assert
    assert (
        colorize("text", GREEN, use_color=False) == "text"
    ), "Plain text should be returned when color is disabled"
    assert GREEN in colorize(
        "text", GREEN, use_color=True
    ), "ANSI color codes should be applied when color is enabled"


def test_supports_color_honors_no_color_env(monkeypatch):
    """NO_COLOR environment variable should disable color support."""
    # Arrange
    monkeypatch.setenv("NO_COLOR", "1")

    # Act / Assert
    assert (
        supports_color() is False
    ), "Color should be disabled when NO_COLOR is set"


def test_format_feedback_messages_without_color():
    """Feedback helpers should produce readable plain-text messages."""
    # Act / Assert
    assert (
        format_correct(use_color=False) == "Correct!"
    ), "Correct feedback should be readable without ANSI codes"
    assert (
        format_incorrect("Answer", use_color=False)
        == "Incorrect. Correct answer: Answer"
    ), "Incorrect feedback should include the expected answer"


def test_display_functions_write_to_terminal(capsys):
    """Display helpers should write formatted output to stdout."""
    # Act
    display_question("DNS")
    display_correct()
    display_incorrect("Domain Name System")
    display_summary(
        {"total": 1, "accuracy_percent": 100.0, "missed_terms": []}
    )
    captured = capsys.readouterr()

    # Assert
    assert "DNS" in captured.out, "Question display should include card front"
    assert "Correct!" in captured.out, "Correct feedback should be displayed"
    assert (
        "Incorrect" in captured.out
    ), "Incorrect feedback should be displayed"
    assert (
        "Session Summary" in captured.out
    ), "Session summary should be displayed"


def test_display_extra_stats_writes_extended_output(capsys):
    """Extended stats should include answer counts, mode, and deck size."""
    display_extra_stats({"correct": 2, "total": 3}, "adaptive", 5)
    output = capsys.readouterr().out

    assert "Correct answers:   2" in output
    assert "Incorrect answers: 1" in output
    assert "Quiz mode:         adaptive" in output
    assert "Deck size:         5" in output


def test_prompt_answer_strips_whitespace(monkeypatch):
    """Prompt helper should strip leading and trailing whitespace."""
    # Arrange
    monkeypatch.setattr("builtins.input", lambda prompt: "  answer  ")

    # Act
    answer = prompt_answer()

    # Assert
    assert answer == "answer", "Prompted answer should be stripped"


def test_supports_color_disables_for_dumb_terminal(monkeypatch):
    """Dumb terminals should not use ANSI color codes."""
    # Arrange
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("TERM", "dumb")

    # Act / Assert
    assert (
        supports_color() is False
    ), "Color should be disabled for dumb terminals"
