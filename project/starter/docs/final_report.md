# AI-Assisted Development Project Report

**Student Name:** Justin Kumpe
**Project Title:** Flashcard Quizzer
**Date:** July 5, 2026

## Executive Summary

I built **Flashcard Quizzer**, a command-line study tool that loads flashcards from JSON files and runs interactive quiz sessions in the terminal. The application extends the Udacity starter codebase—originally a task-manager CRUD demo—into a focused study utility with three quiz modes, session statistics, and robust error handling.

Main features include a dual-format JSON loader, three quiz modes (sequential, random, adaptive), session analytics, optional extended stats via `--stats`, and a terminal UI with ANSI color support and graceful exit handling. Users run sessions with `python main.py -m adaptive -f data/python_basics.json`.

Throughout development, I collaborated with **Cursor (Agent)** using phased, scoped prompts, checklist-driven code review, and documented accept/reject decisions in `ai_edit_log.md`. AI generated scaffolding quickly; I reviewed and modified suggestions that missed edge cases or violated separation of concerns. The final codebase has 51 tests at 92% coverage, all quality tools passing, and two design patterns applied to real architectural needs.

## Project Overview

### Problem Statement

Learners need a simple terminal tool that accepts common JSON deck formats, runs repeatable quiz sessions, and surfaces which terms they still miss—without a GUI or external services.

### Solution Approach

I replaced the starter's task-manager entry point with a modular flashcard quizzer. Key decisions: strict separation of concerns across modules, a callback-driven `QuizEngine` for testability, and fail-fast loading via `FlashcardLoadError`. Stack: Python 3.10+, stdlib, pytest/pytest-cov, Black/isort/flake8/mypy.

### Final Features

- [x] Dual-format JSON flashcard loader with field validation
- [x] Three quiz modes: sequential, random, and adaptive
- [x] Session statistics (accuracy, missed terms) and `--stats` flag
- [x] Colored terminal UI with `NO_COLOR` fallback
- [x] Graceful exit on `exit`, Ctrl+C, and Ctrl+D

## AI Collaboration Experience

### AI Tools Used

- [x] Other: **Cursor (Agent)**

### Collaboration Workflow

1. Scoped each prompt to one module with explicit boundaries ("no quiz logic yet").
2. Used AI for setup, generation, test refactoring, checklist review, and documentation.
3. Validated every output with pytest, manual CLI testing, and `code_review_checklist.md`.
4. Followed up with targeted prompts for specific gaps rather than full regenerations.

### Most Valuable AI Interactions

#### Example 1: Data Loader and Error Handling

**Context:** Build a loader for two JSON formats with validation.  
**AI Prompt:** Create `data_loader.py` with type hints, tests, and checklist review.  
**AI Response:** Helper decomposition, `FlashcardLoadError`, and comprehensive tests.  
**Your Changes:** Rejected silent success on empty decks—now raises `FlashcardLoadError`.  
**Outcome:** Clear errors for missing files, bad JSON, invalid structure, and empty decks.

#### Example 2: Senior Code Review

**Context:** Post-implementation quality pass.  
**AI Prompt:** Review against checklist; fix top three issues.  
**AI Response:** Missing `EOFError` handling, no file-size limit, duplicated mode validation.  
**Your Changes:** Accepted all three; kept "ever missed" semantics for `missed_terms`.  
**Outcome:** Safer loading, consistent mode registry, two new tests.

#### Example 3: Separation of Concerns Refactor

**Context:** `main.py` had absorbed session orchestration.  
**AI Prompt:** Extract quiz logic; keep files under ~200 lines; verify pytest.  
**AI Response:** Created `quiz_session.py`, `quiz_factory.py`; slimmed `main.py`.  
**Your Changes:** Rejected circular re-exports; updated imports to `quiz_factory` directly.  
**Outcome:** Clean module boundaries, 51 passing tests.

### Challenges with AI Collaboration

AI struggled with submission-specific test names, security defaults (file-size limits, empty-deck rejection), and terminal edge cases (EOF vs. Ctrl+C). It also favored `# type: ignore` over proper typing and tended to consolidate logic in entry-point files. Strengths: rapid scaffolding, test deduplication, and systematic checklist reviews. My key improvement was scheduling dedicated review passes after generation, not just during it.

## Software Engineering Practices

### Code Quality Measures

- [x] Code formatting (Black, isort)
- [x] Linting (flake8, mypy)
- [x] Type hints, docstrings, and error handling

### Testing Strategy

Unit tests cover loader validation, quiz modes, engine logic, UI formatting, and integration flows—including edge cases (empty deck, invalid JSON, EOF, unknown mode) and error conditions. Hybrid TDD: loader tests written alongside implementation; engine/UI tests followed features. **Coverage: 92%**, 51 tests passing. Original starter tests preserved.

### Design Patterns Used

- **Strategy** (`utils/quiz_modes.py`): `QuizEngine` delegates card selection to `SequentialMode`, `RandomMode`, or `AdaptiveMode`. Chosen because the quiz loop is identical across modes—only ordering differs.
- **Factory** (`utils/quiz_factory.py`): `QuizModeFactory.create_mode()` instantiates strategies from CLI strings. Chosen to decouple CLI/session code from concrete classes and centralize mode validation.

### Code Structure and Organization

`main.py` parses args; `quiz_session.py` orchestrates; `quiz_engine.py` runs the loop; `ui.py` displays; `data_loader.py` validates I/O. A mid-project refactor extracted orchestration from `main.py` and split the factory after a circular-import incident.

## Technical Challenges and Solutions

### Challenge 1: Empty Valid JSON

**Problem:** AI returned `[]` for empty decks, enabling zero-card sessions.  
**Solution:** Raise `FlashcardLoadError` when no cards exist.  
**AI Involvement:** Checklist review surfaced the gap; I directed the fix.  
**Lessons Learned:** Valid syntax ≠ valid application state.

### Challenge 2: Tooling Conflicts

**Problem:** Black (88 cols) vs. flake8 (79 cols) caused fix ping-pong.  
**Solution:** Aligned config in `pyproject.toml` and `.flake8`.  
**Lessons Learned:** Configure quality tools together before the first format pass.

## Code Quality Analysis

### Metrics

- Test coverage: **92%**
- Tests passing: **51**
- Linting: **0 errors** (black, isort, flake8, mypy)
- Functions/classes (app code): 29

### Self-Assessment

- **Code Readability:** 4 — Small modules, descriptive names, docstrings on public APIs.
- **Code Maintainability:** 4 — Strategy/Factory simplify adding modes; orchestration isolated from CLI.
- **Test Quality:** 4 — Named rubric tests plus parametrized edge groups; `main.py` entry lightly covered.
- **Documentation:** 4 — README and `ai_edit_log.md` cover setup, architecture, and AI decisions.

## Learning Outcomes

**Technical:** Strategy/Factory implementation, parametrized pytest, Python quality toolchain, callback-driven terminal apps.

**AI collaboration:** Scoped prompts with boundaries, checklist review after generation, documented accept/reject reasoning, human ownership of edge cases.

**Engineering:** Patterns reduce change cost when applied to real variation points; testing is part of review, not an afterthought.

## Reflection

Phased prompts and the senior code review pass were most effective—the review found EOFError and file-size gaps I had missed. Extracting `quiz_session.py` produced the cleanest architecture. I would add subprocess tests for `main.py` and align tool config on day one. Future enhancements: deck editing, spaced-repetition scheduling, and session export.

## Conclusion

AI-assisted development means AI accelerates scaffolding while I own review, testing, and architecture. Practices I will continue: scoped prompting, checklist review, test-first validation, and honest documentation of what I accepted, modified, or rejected.

## Appendices

### Appendix A: AI Interaction Log

See `docs/ai_edit_log.md` — eight entries covering setup, loader hardening, quiz architecture, code review, refactor, and quality tooling.

### Appendix B: Code Statistics

51 tests passing | 92% coverage | 16 major AI prompts | ~15–20% of AI code modified

### Appendix C: Resources

`docs/design_patterns.md`, `ai_guidance/code_review_checklist.md`, `docs/project_rubric.md`
