# Flashcard Quizzer

A command-line flashcard study tool built with Python. Load flashcards from
JSON files, quiz yourself in the terminal, and review session statistics when
you finish.

The project demonstrates modular design, design patterns, test-driven
development, and AI-assisted software engineering practices.

## Prerequisites

- Python 3.10 or higher
- pip
- Git (optional)

## Setup

```bash
cd project/starter
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Sample flashcard decks are in `data/`:

- `data/glossary.json` — array format (tech acronyms)
- `data/python_basics.json` — wrapper format (Python basics)

## Usage

Show available options:

```bash
python main.py --help
```

Run a quiz in adaptive mode:

```bash
python main.py -m adaptive -f data/python_basics.json
```

Other examples:

```bash
# Sequential mode (default) — cards in file order
python main.py -f data/glossary.json

# Random mode — shuffled cards (type "exit" to end)
python main.py -m random -f data/glossary.json

# Extended session statistics
python main.py -f data/glossary.json --stats
```

During a session:

- Type your answer and press Enter
- Type `exit` to end early (partial stats are saved)
- Press `Ctrl+C` or `Ctrl+D` to end gracefully

## Quiz Modes

| Mode | Flag | Behavior |
|------|------|----------|
| **Sequential** | `-m sequential` (default) | Cards 1→N in file order; session ends after one pass |
| **Random** | `-m random` | Shuffled order; reshuffles when the deck is exhausted |
| **Adaptive** | `-m adaptive` | Prioritizes cards you missed; repeats until all are correct |

## JSON File Formats

The loader accepts two top-level JSON structures. Every card must have
non-empty string `"front"` and `"back"` fields.

**Array format:**

```json
[
  {"front": "HTTP", "back": "Hypertext Transfer Protocol"},
  {"front": "API", "back": "Application Programming Interface"}
]
```

**Wrapper format:**

```json
{
  "cards": [
    {"front": "len()", "back": "Returns the number of items"},
    {"front": "list", "back": "Ordered mutable sequence"}
  ]
}
```

## Testing

Run all tests:

```bash
python -m pytest
```

Run tests with an HTML coverage report (target: >80% coverage):

```bash
python -m pytest --cov=. --cov-report=html
open htmlcov/index.html
```

Run a specific test file:

```bash
python -m pytest tests/test_quiz_modes.py -v
```

## Code Quality

```bash
black .
isort .
flake8 .
mypy .
```

## Architecture

Responsibilities are separated across focused modules:

| Module | Role |
|--------|------|
| `main.py` | CLI argument parsing |
| `utils/data_loader.py` | Load and validate JSON flashcard files |
| `utils/quiz_factory.py` | Create quiz mode strategies by name |
| `utils/quiz_modes.py` | Card selection algorithms (Strategy pattern) |
| `utils/quiz_engine.py` | Quiz loop, answer checking, session stats |
| `utils/quiz_session.py` | Orchestrates loader, engine, and UI |
| `utils/ui.py` | Terminal display and user prompts |

### Design Patterns

**Strategy Pattern** (`utils/quiz_modes.py`) — `QuizEngine` delegates card
selection to interchangeable `QuizMode` strategies (`SequentialMode`,
`RandomMode`, `AdaptiveMode`) without changing its core quiz loop.

**Factory Pattern** (`utils/quiz_factory.py`) — `QuizModeFactory.create_mode()`
instantiates the correct strategy from a user-facing mode string, keeping the
CLI decoupled from concrete mode classes.

## Project Structure

```
starter/
├── main.py                    # CLI entry point
├── data/                      # Sample flashcard JSON files
├── utils/
│   ├── data_loader.py         # JSON loading and validation
│   ├── quiz_modes.py          # Strategy pattern — quiz modes
│   ├── quiz_factory.py        # Factory pattern — mode creation
│   ├── quiz_engine.py         # Quiz logic and statistics
│   ├── quiz_session.py        # Session orchestration
│   ├── ui.py                  # Terminal UI
│   └── exceptions.py          # Custom exceptions
├── tests/                     # Unit and integration tests
├── docs/                      # Project documentation templates
├── ai_guidance/               # AI prompting and review guides
├── requirements.txt
└── README.md
```

## Built With

- [Python](https://www.python.org/)
- [pytest](https://docs.pytest.org/) / [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Black](https://black.readthedocs.io/) / [isort](https://pycqa.github.io/isort/) / [flake8](https://flake8.pycqa.org/) / [mypy](https://mypy.readthedocs.io/)

## License

See [LICENSE.txt](LICENSE.txt).
