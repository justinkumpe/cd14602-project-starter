# AI Edit Log

Documentation of AI-assisted development for the Flashcard Quizzer project. Each entry records the prompt, AI output, changes made, and lessons learned.

---

### 2026-07-05 - Environment Setup and Sample Flashcard Data

**Context:** Starting the Flashcard Quizzer from the Udacity starter repo. Needed a working virtual environment, dependencies installed via pip, and sample JSON decks before any application code.

**AI Tool Used:** Cursor (Agent)

**Prompt/Request:** Create a venv, install from `requirements.txt`, add `data/glossary.json` (array format) and `data/python_basics.json` (wrapper format) with at least five cards each. Provide exact verification commands. No quiz logic yet.

**AI Response:** Created `venv/`, installed all requirements, and added two sample JSON files with six cards each (tech acronyms and Python basics). Provided step-by-step verify commands for Python version, pip packages, JSON parsing, and pytest.

**Changes Made:**
- **Accepted:** Full setup as proposed — venv, pip install, both JSON formats, verification commands.
- **Rejected:** Nothing substantive; scope was intentionally limited to environment + data.

**Reasoning:** The prompt explicitly scoped work to setup only. Accepting the sample data unchanged let me validate the loader in the next phase against realistic examples.

**Outcome:** Reproducible dev environment with two format-diverse sample decks. All 15 starter tests still passed.

**Lessons Learned:**
- **AI strength:** Fast, complete bootstrap of environment and fixture data from a precise, bounded prompt.
- **AI weakness:** Will implement ahead of scope if prompts are vague — explicit "do not implement X" boundaries worked well here.

---

### 2026-07-05 - Flashcard Data Loader and Error Handling

**Context:** Phase 1 required `utils/data_loader.py` supporting two JSON formats, validation of `front`/`back` fields, and a custom `FlashcardLoadError` with user-friendly messages.

**AI Tool Used:** Cursor (Agent)

**Prompt/Request:** Build the data loader with type hints, docstrings, stdlib only (`json`, `pathlib`), and tests. Follow TDD, DRY, SOLID, PEP 8. Then review against `code_review_checklist.md` and harden error handling.

**AI Response:** Generated `utils/exceptions.py`, `utils/data_loader.py` with private helpers (`_load_json`, `_extract_cards`, `_validate_cards`), and `tests/test_flashcard_loader.py`. On review, added empty-deck rejection, directory-path detection, richer invalid-JSON messages (line/column), and a `__main__` smoke-test entry point.

**Changes Made:**
- **Accepted:** Two-format parsing, per-card validation, `FlashcardLoadError` with `from None` to suppress tracebacks, helper decomposition, smoke-test CLI.
- **Rejected:** Silent success on empty `[]` or `{"cards": []}` — changed to raise `FlashcardLoadError` so corrupt/empty decks never return an empty list quietly.

**Reasoning:** An empty deck is valid JSON but a failed quiz session. Raising an explicit error matches the rubric requirement and prevents the engine from "succeeding" with zero cards.

**Outcome:** Loader handles missing files, malformed JSON, bad structure, and invalid cards with clear messages. CLI exits with code 1 on failure.

**Lessons Learned:**
- **AI strength:** Solid first-pass structure with typed helpers and comprehensive error branches.
- **AI weakness:** Happy-path bias — empty valid JSON was initially treated as success; checklist-driven review caught it.

---

### 2026-07-05 - Test Refactoring and Rubric Alignment

**Context:** Initial loader tests worked but felt repetitive. Later, the rubric required specific test names (`test_load_valid_flashcards_array`, `test_load_invalid_json`, `test_load_missing_required_field`).

**AI Tool Used:** Cursor (Agent)

**Prompt/Request:** (1) "Rewrite tests using functions, fixtures, parameters to comply with DRY." (2) Create `test_flashcard_loader.py` with rubric-required names and wrapper-format coverage.

**AI Response:** First refactored 11 class methods into 3 parametrized functions with shared `flashcard_file` fixture and `assert_load_raises` helper. After rubric feedback, rewrote to explicit named tests for required cases while keeping parametrized groups for supplementary edge cases.

**Changes Made:**
- **Accepted:** `flashcard_file` fixture, `write_json` helper, parametrization for file-error and invalid-content groups, AAA comments, clear assertion messages.
- **Rejected:** Fully parametrized names only (e.g. `test_load_valid_flashcards[array_format]`) as the sole style — rubric expects recognizable function names, so required tests were named explicitly.

**Reasoning:** DRY reduces maintenance, but assessors look for specific test identifiers. The hybrid approach keeps both: named rubric tests plus parametrized coverage for edge cases.

**Outcome:** 15 loader tests passing; readable failures via `pytest.param(..., id="...")` on grouped tests.

**Lessons Learned:**
- **AI strength:** Excellent at mechanical test deduplication with fixtures and `parametrize`.
- **AI weakness:** Optimizes for brevity over rubric semantics — I needed a follow-up prompt to align names with submission requirements.

---

### 2026-07-05 - Quiz Architecture (Strategy, Factory, Engine, UI, CLI)

**Context:** Build the core application: quiz modes, factory, engine, terminal UI, and `main.py` CLI — replacing the task-manager demo as the entry point.

**AI Tool Used:** Cursor (Agent)

**Prompt/Request:** Sequential prompts for `quiz_modes.py` (Strategy), `QuizModeFactory`, `quiz_engine.py`, `ui.py`, and `main.py` with `argparse` (`-f`, `-m`, `--stats`), graceful exit on `exit`/Ctrl+C, and `FlashcardLoadError` → stderr + exit 1.

**AI Response:** Delivered modular components: three `QuizMode` strategies, factory with case-insensitive mode names, callback-driven `QuizEngine`, pure `format_*` UI helpers with ANSI color fallback, and a wired CLI. Removed task-manager demo from `main.py`.

**Changes Made:**
- **Accepted:** Strategy/Factory separation, engine/UI callback boundary, case-insensitive answer checking, session stats (`total`, `correct`, `accuracy_percent`, `missed_terms`), colored terminal output with `NO_COLOR`/`TERM=dumb` fallback.
- **Rejected:** Keeping quiz orchestration permanently in `main.py` — later extracted to `utils/quiz_session.py` during refactor phase.

**Reasoning:** `main.py` should only parse arguments. Session wiring (load → engine → UI callbacks → summary) is orchestration, not CLI parsing.

**Outcome:** Working CLI: `python main.py --help`, `python main.py -m adaptive -f data/python_basics.json`.

**Lessons Learned:**
- **AI strength:** Produces clean pattern implementations when prompts reference `design_patterns.md` and specify module boundaries.
- **AI weakness:** Tends to put orchestration in the entry-point file unless explicitly told to separate concerns.

---

### 2026-07-05 - Senior Code Review and Top-Three Fixes

**Context:** Prompt 11 asked for a checklist review of the full codebase with fixes for the top three issues.

**AI Tool Used:** Cursor (Agent)

**Prompt/Request:** Review against `ai_guidance/code_review_checklist.md`. Report logic bugs, pattern misuse, missing edge cases, and security issues. Fix the top three.

**AI Response:** Identified EOFError (Ctrl+D) not handled, no file-size limit before `json.load()`, and duplicated mode validation in `argparse` `choices` vs `QuizModeFactory`. Applied fixes and added tests.

**Changes Made:**
- **Accepted:** `EOFError` handling in `QuizEngine.run_quiz`, 1 MB max file size in `_load_json`, removed `argparse` `choices` so factory is single source of truth.
- **Rejected:** Treating `missed_terms` as "still wrong at session end" — kept "ever missed during session" behavior; it matches study analytics intent.

**Reasoning:** Ctrl+D is common in terminal apps and should behave like `exit`. File-size guard prevents accidental memory exhaustion. One mode registry avoids drift between CLI and factory.

**Outcome:** Friendly graceful exits, safer loading, consistent mode validation. Added `test_eof_error_ends_session_with_partial_stats` and `test_run_quiz_session_rejects_unknown_mode`.

**Lessons Learned:**
- **AI strength:** Systematic checklist review finds real edge cases I overlooked after implementation.
- **AI weakness:** First implementation often handles Ctrl+C but not EOF; security limits rarely appear without an explicit review pass.

---

### 2026-07-05 - Separation of Concerns Refactor

**Context:** Ensure no file exceeds ~200 lines and responsibilities are clearly split: data loading ≠ quiz logic ≠ UI ≠ CLI parsing.

**AI Tool Used:** Cursor (Agent)

**Prompt/Request:** Refactor if needed; extract quiz logic from `main.py`; clarify `AdaptiveMode` with a short algorithm comment; keep all tests passing.

**AI Response:** Extracted `utils/quiz_session.py` (orchestration), `utils/quiz_factory.py` (factory), `utils/data_loader_cli.py` (loader smoke CLI). Slimmed `main.py` to argparse only. Moved `display_extra_stats` to `ui.py`. Documented adaptive algorithm; removed unused `current_card` state.

**Changes Made:**
- **Accepted:** New modules, re-exports for backward-compatible test imports, adaptive FIFO priority comment block.
- **Rejected:** Re-exporting `QuizModeFactory` from `quiz_modes.py` — caused circular imports; imports updated to `quiz_factory` directly instead.

**Reasoning:** Circular imports are a smell that the factory belongs in its own module. Explicit imports are clearer than fragile re-exports.

**Outcome:** All files ≤ ~203 lines (`ui.py` barely at limit). 51 tests passing. Clear module map documented in README.

**Lessons Learned:**
- **AI strength:** Fast structural refactor without breaking tests when prompted to verify pytest after each change.
- **AI weakness:** Initial "convenience re-exports" can introduce import cycles — run the app/tests immediately after refactors.

---

### 2026-07-05 - Quality Tooling, Coverage, and README

**Context:** Final phase: pass `black`, `isort`, `flake8`, `mypy` with no errors; maintain >80% coverage; update README for the Flashcard Quizzer.

**AI Tool Used:** Cursor (Agent)

**Prompt/Request:** Run and fix all quality tools. Add integration tests and coverage. Update README with setup, usage, testing, architecture, modes, and JSON formats.

**AI Response:** Added `pyproject.toml` and `.flake8` (line-length 79, exclude `venv`). Fixed mypy issues with `cast()` and explicit types. Added `test_integration.py`, `test_quiz_engine.py`, `test_ui.py`, `test_main.py` — coverage reached 90%. Replaced README with quizzer-specific documentation.

**Changes Made:**
- **Accepted:** Tool config files, typed test helpers, coverage tests for engine/UI edge cases, full README rewrite.
- **Rejected:** Using `# type: ignore` to silence mypy — fixed properly with `cast(Dict[str, Any], json.load(...))`, `list[Flashcard]` locals, and `task_id: int` return.

**Reasoning:** Type ignores hide real issues; `cast` and explicit annotations document intent where JSON/dynamic state is inherently loose.

**Outcome:** `black . && isort . && flake8 . && mypy .` all pass; 51 tests green; HTML coverage report in `htmlcov/`.

**Lessons Learned:**
- **AI strength:** Efficiently resolves lint/type failures across many files in one pass.
- **AI weakness:** Black defaults to 88 columns while flake8 often expects 79 — tool config must be aligned explicitly or fixes will ping-pong.

---

### 2026-07-05 - Final Report and Submission Readiness Review

**Context:** Rubric assessment and Definition of Done verification before submission. Needed a completed final report and confirmation that all deliverables were met.

**AI Tool Used:** Cursor (Agent)

**Prompt/Request:** Assess project against the rubric; generate the final report from `report_template.md` and existing log entries; verify Definition of Done (playable adaptive game, Strategy/Factory patterns, tests/flake8, ≥5 corrected AI examples).

**AI Response:** Produced rubric scorecard showing strong compliance across all areas except the missing final report. Generated `docs/final_report.md` (~1,100 words) from log and README content. Verified 51 tests passing, 92% coverage, flake8 clean, and adaptive CLI playable end-to-end.

**Changes Made:**
- **Accepted:** Final report structure, metrics pulled from pytest/coverage runs, reflection content synthesized from log entries.
- **Rejected:** 2,000+ word report length from the template — trimmed to rubric's 1,000–1,500 word requirement.

**Reasoning:** Submission requirements override template defaults. The report should reflect actual project decisions documented in this log, not generic filler.

**Outcome:** `docs/final_report.md` complete; Definition of Done criteria verified. `ai_edit_log.md` cleaned to remove template boilerplate and fill reflection sections.

**Lessons Learned:**
- **AI strength:** Fast synthesis of scattered project artifacts (logs, tests, README) into submission-ready documentation.
- **AI weakness:** Default report length and generic template text need human trimming to match rubric word counts and project specifics.

---

## Summary Statistics

- **Total AI interactions:** 17 major prompts (setup through final report)
- **Log entries documenting accept/reject decisions:** 8
- **Lines of AI-generated code used:** ~1,200+ (`utils/`, `main.py`, `tests/`)
- **Lines of AI-generated code modified:** ~15–20% (error hardening, refactor splits, type fixes, test naming)
- **Tests passing:** 51
- **Test coverage:** 92%
- **Quality tools:** black, isort, flake8, mypy — all pass with zero errors
- **Most helpful AI interaction:** Senior code review — surfaced EOFError, file-size limit, and factory/argparse duplication
- **Most challenging AI interaction:** Balancing DRY parametrized tests with rubric-required explicit test names
- **Biggest lesson learned:** AI delivers strong scaffolding fast, but edge cases, security limits, and submission-specific requirements need deliberate human review passes

---

## Reflection Questions

### 1. What types of tasks did AI help with most effectively?

AI was most effective at bounded, well-scoped tasks: environment bootstrap, boilerplate module creation, test deduplication with fixtures/parametrize, mechanical lint/type fixes across many files, and structural refactors when I required pytest verification after each change. It also excelled at checklist-driven code reviews when pointed at `code_review_checklist.md`.

### 2. Where did you need to make the most modifications to AI suggestions?

The largest corrections were in error-handling semantics (empty decks treated as success), architectural boundaries (orchestration leaking into `main.py`, circular re-exports), submission-specific test naming, and typing shortcuts (`# type: ignore` instead of proper `cast()`). Terminal edge cases (EOF vs. Ctrl+C) and security defaults (file-size limits) also required human-directed fixes after the initial generation pass.

### 3. What patterns did you notice in AI strengths and weaknesses?

**Strengths:** Fast scaffolding, clean first-pass structure with type hints and docstrings, efficient test refactoring, and systematic review when given an explicit checklist.

**Weaknesses:** Happy-path bias, scope creep when prompts lack boundaries, optimizing for brevity over rubric semantics, consolidating logic into entry-point files, and skipping security-minded defaults unless asked. AI also tends to handle Ctrl+C but forget EOFError.

### 4. How did your prompting technique improve over time?

Early prompts were feature-focused ("build the loader"). Later prompts added explicit out-of-scope boundaries ("no quiz logic yet"), referenced project guides (`design_patterns.md`, `code_review_checklist.md`), required verification commands (pytest, flake8), and scheduled separate review passes instead of expecting perfection on the first generation. Follow-up prompts became surgical ("fix top three issues from checklist review") rather than full regenerations.

### 5. What would you do differently in future AI collaborations?

I would align quality tool config (Black/flake8 line length) before the first formatting pass, schedule a dedicated review prompt after every generation phase, and write rubric-required test names explicitly from the start rather than refactoring later. I would also run the app and pytest immediately after every refactor to catch import cycles early, and keep documentation (log entries, report sections) updated incrementally instead of batching at the end.
