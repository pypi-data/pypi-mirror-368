"""Mixin for managing progress prompt responses."""
from typing import Any, Optional, List

from wexample_prompt.responses.interactive.progress_prompt_response import ProgressPromptResponse
from wexample_prompt.progress.step_progress_context import ProgressStep


class ProgressPromptResponseManagerMixin:
    """Mixin class for managing progress prompt responses."""

    def progress(
        self,
        total: int,
        current: int,
        width: int = 50,
        label: Optional[str] = None,
        **kwargs: Any
    ) -> ProgressPromptResponse:
        """Create a progress bar.

        Args:
            total: Total number of items
            current: Current progress
            width: Width of the progress bar in characters
            label: Optional label to show above the progress bar
            **kwargs: Additional arguments passed to create_progress
        """
        response = ProgressPromptResponse.create_progress(
            total=total,
            current=current,
            width=width,
            label=label,
            context=self.create_context(),
            **kwargs
        )
        self.print_response(response)
        return response

    def progress_steps(
        self,
        steps: List[ProgressStep],
        width: int = 50,
        title: Optional[str] = None,
        **kwargs: Any
    ) -> ProgressPromptResponse:
        """Create a step-based progress bar.

        Args:
            steps: List of progress steps to execute
            width: Width of the progress bar
            title: Optional title for the progress bar
            **kwargs: Additional arguments passed to create_steps
        """
        context = ProgressPromptResponse.create_steps(
            steps=steps,
            width=width,
            title=title,
            context=self.create_context(),
            **kwargs
        )
        return context

    def progress_execute(
        self,
        callbacks: List[Any],
        width: int = 50,
        title: Optional[str] = None,
        **kwargs: Any
    ) -> List[Any]:
        """Execute a list of callbacks with progress tracking.

        Args:
            callbacks: List of callback functions to execute
            width: Width of the progress bar
            title: Optional title for the progress bar
            **kwargs: Additional arguments passed to execute
        """
        return ProgressPromptResponse.execute(
            callbacks=callbacks,
            width=width,
            title=title,
            context=self.create_context(),
            **kwargs
        )
