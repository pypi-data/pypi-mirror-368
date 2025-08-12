"""Mixin for managing directory picker prompt responses."""
from typing import Any, Optional

from wexample_prompt.responses.interactive.dir_picker_prompt_response import DirPickerPromptResponse


class DirPickerPromptResponseManagerMixin:
    """Mixin class for managing directory picker prompt responses."""

    def dir_picker(
        self,
        question: str = "Select a directory:",
        base_dir: Optional[str] = None,
        abort: Optional[str] = "> Abort",
        **kwargs: Any
    ) -> "DirPickerPromptResponse":
        """Create and execute a directory picker prompt.

        Args:
            question: The question to display
            base_dir: Starting directory (defaults to current working directory)
            abort: Optional abort choice text
            **kwargs: Additional arguments for inquirer.select

        Returns:
            str: Full path to selected directory, or None if aborted
        """
        response = DirPickerPromptResponse.create_dir_picker(
            question=question,
            base_dir=base_dir,
            abort=abort,
            **kwargs
        )
        self.print_response(response)
        return response
