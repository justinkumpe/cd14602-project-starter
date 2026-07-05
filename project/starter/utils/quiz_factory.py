"""
Factory for creating quiz mode strategy instances.

The Factory Pattern centralizes mode creation so callers request modes by name
without importing concrete strategy classes.
"""

from utils.quiz_modes import AdaptiveMode, QuizMode, RandomMode, SequentialMode


class QuizModeFactory:
    """Create ``QuizMode`` strategy instances from user-facing mode names."""

    _MODES: dict[str, type[QuizMode]] = {
        "sequential": SequentialMode,
        "random": RandomMode,
        "adaptive": AdaptiveMode,
    }

    @staticmethod
    def create_mode(mode_name: str) -> QuizMode:
        """
        Create a quiz mode strategy for the given mode name.

        Args:
            mode_name: One of ``sequential``, ``random``, or ``adaptive``
                (case-insensitive).

        Returns:
            A concrete ``QuizMode`` strategy instance.

        Raises:
            ValueError: If ``mode_name`` is not a supported quiz mode.
        """
        normalized_name = mode_name.strip().lower()
        mode_class = QuizModeFactory._MODES.get(normalized_name)

        if mode_class is None:
            supported_modes = ", ".join(sorted(QuizModeFactory._MODES))
            raise ValueError(
                f"Unknown quiz mode '{mode_name}'. "
                f"Supported modes: {supported_modes}."
            )

        return mode_class()
