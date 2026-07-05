#!/usr/bin/env python3
"""
Validate Flashcard Quizzer submission against the project rubric.

Checks code-quality tooling results (when invoked after those tools run),
documentation requirements, design patterns, and other automatable criteria.
Exits 0 when all checks pass, 1 otherwise.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_TEST_NAMES = (
    "test_load_valid_flashcards_array",
    "test_load_invalid_json",
    "test_load_missing_required_field",
)

REQUIRED_REPORT_SECTIONS = (
    "Executive Summary",
    "AI Collaboration",
    "Design Patterns",
    "Reflection",
)

REQUIRED_README_KEYWORDS = ("Setup", "Usage", "Testing", "pytest")

FEATURE_MODULES = (
    "utils/data_loader.py",
    "utils/quiz_engine.py",
    "utils/quiz_modes.py",
    "utils/quiz_session.py",
    "utils/ui.py",
)


@dataclass
class CheckResult:
    """Single rubric check outcome."""

    category: str
    name: str
    passed: bool
    detail: str


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _word_count(text: str) -> int:
    return len(text.split())


def check_required_files() -> list[CheckResult]:
    """Documentation and submission files must exist."""
    results: list[CheckResult] = []
    required = {
        "AI interaction log": ROOT / "docs/ai_edit_log.md",
        "Final report": ROOT / "docs/final_report.md",
        "README": ROOT / "README.md",
        "Code review checklist": ROOT / "ai_guidance/code_review_checklist.md",
        "Main entry point": ROOT / "main.py",
        "Requirements": ROOT / "requirements.txt",
    }
    for label, path in required.items():
        results.append(
            CheckResult(
                "Documentation",
                label,
                path.is_file(),
                (
                    str(path.relative_to(ROOT))
                    if path.is_file()
                    else f"missing: {path}"
                ),
            )
        )
    return results


def check_ai_edit_log() -> list[CheckResult]:
    """AI log must have >=5 dated entries with accept/reject evidence."""
    results: list[CheckResult] = []
    path = ROOT / "docs/ai_edit_log.md"
    text = _read(path)

    dated_entries = re.findall(
        r"^### \d{4}-\d{2}-\d{2} - ", text, re.MULTILINE
    )
    results.append(
        CheckResult(
            "AI Collaboration",
            "At least 5 AI interaction log entries",
            len(dated_entries) >= 5,
            f"found {len(dated_entries)} dated entries",
        )
    )

    has_prompts = "**Prompt/Request:**" in text
    results.append(
        CheckResult(
            "AI Collaboration",
            "Log documents prompts and responses",
            has_prompts and "**AI Response:**" in text,
            (
                "Prompt/Request and AI Response sections present"
                if has_prompts
                else "missing prompt/response sections"
            ),
        )
    )

    rejections = re.findall(
        r"- \*\*Rejected:\*\* (.+)",
        text,
    )
    substantive_rejections = [
        item
        for item in rejections
        if "nothing substantive" not in item.lower()
    ]
    results.append(
        CheckResult(
            "AI Collaboration",
            "Evidence of modifying or rejecting AI suggestions",
            len(substantive_rejections) >= 3,
            (
                f"found {len(substantive_rejections)} substantive "
                "reject/modify notes"
            ),
        )
    )

    has_reasoning = "**Reasoning:**" in text
    results.append(
        CheckResult(
            "AI Collaboration",
            "Decision-making process documented",
            has_reasoning,
            (
                "Reasoning sections present"
                if has_reasoning
                else "missing Reasoning"
            ),
        )
    )
    return results


def check_final_report() -> list[CheckResult]:
    """Final report word count and required sections."""
    results: list[CheckResult] = []
    path = ROOT / "docs/final_report.md"
    text = _read(path)
    words = _word_count(text)

    results.append(
        CheckResult(
            "Documentation",
            "Final report word count (1000-1500)",
            1000 <= words <= 1500,
            f"{words} words",
        )
    )

    missing_sections = [
        section for section in REQUIRED_REPORT_SECTIONS if section not in text
    ]
    results.append(
        CheckResult(
            "Documentation",
            "Final report required sections",
            not missing_sections,
            (
                "all present"
                if not missing_sections
                else f"missing: {', '.join(missing_sections)}"
            ),
        )
    )
    return results


def check_readme() -> list[CheckResult]:
    """README must document setup, usage, and testing."""
    text = _read(ROOT / "README.md")
    missing = [
        keyword for keyword in REQUIRED_README_KEYWORDS if keyword not in text
    ]
    return [
        CheckResult(
            "Documentation",
            "README setup, usage, and testing docs",
            not missing,
            (
                "all keywords present"
                if not missing
                else f"missing keywords: {', '.join(missing)}"
            ),
        )
    ]


def check_design_patterns() -> list[CheckResult]:
    """Strategy and Factory patterns must be implemented."""
    results: list[CheckResult] = []
    quiz_modes = _read(ROOT / "utils/quiz_modes.py")
    quiz_factory = _read(ROOT / "utils/quiz_factory.py")
    final_report = _read(ROOT / "docs/final_report.md")

    results.append(
        CheckResult(
            "Design Patterns",
            "Strategy pattern (QuizMode ABC + modes)",
            "class QuizMode(ABC)" in quiz_modes
            and "class SequentialMode" in quiz_modes
            and "class AdaptiveMode" in quiz_modes,
            "utils/quiz_modes.py",
        )
    )
    results.append(
        CheckResult(
            "Design Patterns",
            "Factory pattern (QuizModeFactory)",
            "class QuizModeFactory" in quiz_factory
            and "create_mode" in quiz_factory,
            "utils/quiz_factory.py",
        )
    )
    results.append(
        CheckResult(
            "Design Patterns",
            "Pattern choice documented in final report",
            "Strategy" in final_report and "Factory" in final_report,
            "final_report.md mentions Strategy and Factory",
        )
    )
    return results


def check_application_features() -> list[CheckResult]:
    """Application extends starter with multiple new feature modules."""
    missing = [
        module for module in FEATURE_MODULES if not (ROOT / module).is_file()
    ]
    return [
        CheckResult(
            "Application",
            "At least 3 new feature modules beyond starter CRUD",
            len(FEATURE_MODULES) - len(missing) >= 3,
            f"{len(FEATURE_MODULES) - len(missing)} feature modules present",
        )
    ]


def check_required_tests() -> list[CheckResult]:
    """Rubric-required loader test names must exist."""
    loader_tests = _read(ROOT / "tests/test_flashcard_loader.py")
    missing = [
        name
        for name in REQUIRED_TEST_NAMES
        if f"def {name}" not in loader_tests
    ]
    return [
        CheckResult(
            "Testing",
            "Rubric-required flashcard loader test names",
            not missing,
            "all present" if not missing else f"missing: {', '.join(missing)}",
        )
    ]


def check_docstrings() -> list[CheckResult]:
    """Public modules should define docstrings on key symbols."""
    results: list[CheckResult] = []
    modules = [
        ROOT / "utils/data_loader.py",
        ROOT / "utils/quiz_engine.py",
        ROOT / "utils/quiz_factory.py",
        ROOT / "main.py",
    ]
    for module_path in modules:
        text = _read(module_path)
        has_module_doc = text.lstrip().startswith(
            '"""'
        ) or text.lstrip().startswith("'''")
        results.append(
            CheckResult(
                "Code Quality",
                f"Module docstring: {module_path.name}",
                has_module_doc,
                str(module_path.relative_to(ROOT)),
            )
        )
    return results


def check_cli_smoke() -> list[CheckResult]:
    """CLI entry point should respond to --help."""
    try:
        completed = subprocess.run(
            [sys.executable, "main.py", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return [
            CheckResult(
                "Application",
                "CLI responds to --help",
                False,
                str(error),
            )
        ]

    passed = (
        completed.returncode == 0 and "Flashcard Quizzer" in completed.stdout
    )
    return [
        CheckResult(
            "Application",
            "CLI responds to --help",
            passed,
            f"exit code {completed.returncode}",
        )
    ]


def run_all_checks() -> list[CheckResult]:
    """Run every automatable rubric check."""
    results: list[CheckResult] = []
    results.extend(check_required_files())
    results.extend(check_ai_edit_log())
    results.extend(check_final_report())
    results.extend(check_readme())
    results.extend(check_design_patterns())
    results.extend(check_application_features())
    results.extend(check_required_tests())
    results.extend(check_docstrings())
    results.extend(check_cli_smoke())
    return results


def print_report(results: list[CheckResult]) -> None:
    """Print a rubric scorecard grouped by category."""
    categories: dict[str, list[CheckResult]] = {}
    for result in results:
        categories.setdefault(result.category, []).append(result)

    print("Project Rubric Validation")
    print("=" * 60)
    for category, checks in categories.items():
        print(f"\n{category}")
        print("-" * len(category))
        for check in checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"  [{status}] {check.name}: {check.detail}")

    passed = sum(1 for result in results if result.passed)
    total = len(results)
    print("\n" + "=" * 60)
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("Rubric validation: PASSED")
    else:
        print("Rubric validation: FAILED")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate project rubric criteria."
    )
    parser.parse_args()

    results = run_all_checks()
    print_report(results)
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
