"""Tests for quiz session orchestration."""

import pytest

from utils.quiz_session import run_quiz_session


@pytest.fixture
def deck_file(tmp_path) -> str:
    """Write a two-card deck and return its path."""
    path = tmp_path / "deck.json"
    path.write_text(
        '[{"front": "Q1", "back": "A1"}, {"front": "Q2", "back": "A2"}]',
        encoding="utf-8",
    )
    return str(path)


def _mock_ui(monkeypatch, answers: list[str]) -> None:
    """Replace UI helpers with deterministic non-interactive behavior."""
    answer_iter = iter(answers)
    monkeypatch.setattr(
        "utils.quiz_session.ui.prompt_answer",
        lambda prompt="": next(answer_iter),
    )
    monkeypatch.setattr(
        "utils.quiz_session.ui.display_question", lambda front: None
    )
    monkeypatch.setattr("utils.quiz_session.ui.display_correct", lambda: None)
    monkeypatch.setattr(
        "utils.quiz_session.ui.display_incorrect", lambda back: None
    )


def test_run_quiz_session_records_summary(deck_file, monkeypatch):
    """Successful sessions should finish with accurate session statistics."""
    summaries: list[dict[str, object]] = []
    _mock_ui(monkeypatch, ["A1", "wrong"])
    monkeypatch.setattr(
        "utils.quiz_session.ui.display_summary",
        lambda stats: summaries.append(stats),
    )

    exit_code = run_quiz_session(deck_file, "sequential")

    assert exit_code == 0
    assert summaries[0]["total"] == 2
    assert summaries[0]["correct"] == 1
    assert summaries[0]["missed_terms"] == ["Q2"]


def test_run_quiz_session_with_stats_shows_extra_output(
    deck_file, monkeypatch
):
    """The --stats flag should trigger extended session statistics."""
    extra_stats_calls: list[tuple[str, int]] = []
    _mock_ui(monkeypatch, ["A1", "A2"])
    monkeypatch.setattr(
        "utils.quiz_session.ui.display_summary", lambda stats: None
    )
    monkeypatch.setattr(
        "utils.quiz_session.ui.display_extra_stats",
        lambda stats, mode, size: extra_stats_calls.append((mode, size)),
    )

    run_quiz_session(deck_file, "sequential", show_stats=True)

    assert extra_stats_calls == [("sequential", 2)]


def test_run_quiz_session_rejects_missing_file(tmp_path, capsys):
    """Missing deck files should print a friendly error and exit 1."""
    exit_code = run_quiz_session(str(tmp_path / "missing.json"), "sequential")

    assert exit_code == 1
    assert "not found" in capsys.readouterr().err


def test_run_quiz_session_rejects_unknown_mode(deck_file, capsys):
    """Unknown quiz modes should fail via the factory with exit code 1."""
    exit_code = run_quiz_session(deck_file, "chaos")

    assert exit_code == 1
    assert "Unknown quiz mode" in capsys.readouterr().err


def test_run_quiz_session_handles_keyboard_interrupt(
    deck_file, monkeypatch, capsys
):
    """Ctrl+C during a session should end gracefully with partial stats."""
    call_count = 0

    def prompt(_: str = "") -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return "A1"
        raise KeyboardInterrupt

    monkeypatch.setattr("utils.quiz_session.ui.prompt_answer", prompt)
    monkeypatch.setattr(
        "utils.quiz_session.ui.display_question", lambda front: None
    )
    monkeypatch.setattr("utils.quiz_session.ui.display_correct", lambda: None)
    monkeypatch.setattr(
        "utils.quiz_session.ui.display_incorrect", lambda back: None
    )
    monkeypatch.setattr(
        "utils.quiz_session.ui.display_summary", lambda stats: None
    )

    exit_code = run_quiz_session(deck_file, "sequential")

    assert exit_code == 0
    assert "Session ended." in capsys.readouterr().out
