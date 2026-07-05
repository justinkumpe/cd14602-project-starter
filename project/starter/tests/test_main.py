"""Tests for the Flashcard Quizzer CLI entry point."""

import pytest

import main as cli_main


def test_build_parser_requires_file_flag():
    """The file argument is required for every quiz run."""
    with pytest.raises(SystemExit):
        cli_main.build_parser().parse_args([])


def test_build_parser_defaults():
    """Parser should default to sequential mode without extended stats."""
    args = cli_main.build_parser().parse_args(["-f", "deck.json"])

    assert args.file == "deck.json"
    assert args.mode == "sequential"
    assert args.stats is False


def test_build_parser_accepts_mode_and_stats():
    """Parser should accept explicit mode and --stats flags."""
    args = cli_main.build_parser().parse_args(
        ["-f", "deck.json", "-m", "adaptive", "--stats"]
    )

    assert args.mode == "adaptive"
    assert args.stats is True


def test_main_delegates_to_run_quiz_session(monkeypatch):
    """main() should pass parsed CLI args to run_quiz_session."""
    captured: dict[str, object] = {}

    def fake_run(file_path: str, mode_name: str, show_stats: bool) -> int:
        captured["file"] = file_path
        captured["mode"] = mode_name
        captured["stats"] = show_stats
        return 0

    monkeypatch.setattr(cli_main, "run_quiz_session", fake_run)

    exit_code = cli_main.main(
        ["-f", "data/deck.json", "-m", "random", "--stats"]
    )

    assert exit_code == 0
    assert captured == {
        "file": "data/deck.json",
        "mode": "random",
        "stats": True,
    }
