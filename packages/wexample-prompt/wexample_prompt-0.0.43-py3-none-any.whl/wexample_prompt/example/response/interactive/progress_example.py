"""Example usage of ProgressPromptResponse."""
import time
from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.progress.step_progress_context import ProgressStep
from wexample_prompt.responses.interactive.progress_prompt_response import ProgressPromptResponse


def step1() -> None:
    """First step: Initialize system."""
    time.sleep(0.5)


def step2() -> None:
    """Second step: Process data."""
    time.sleep(1)


def step3() -> None:
    """Third step: Cleanup."""
    time.sleep(0.5)


class ProgressExample(AbstractResponseExample):
    """Example usage of progress responses."""

    def example_class(self, indentation: Optional[int] = None):
        """Example using the response class directly."""
        return ProgressPromptResponse.create_progress(
            total=5,
            current=3,
            label="Processing",
            context=self.io_manager.create_context(indentation=indentation)
        )

    def example_manager(self):
        """Example using the IoManager."""
        self.io_manager.progress(
            total=5,
            current=3,
            label="Processing"
        )

    def example_context(self):
        """Example using a context class."""
        self.class_with_context.progress(
            total=5,
            current=3,
            label="Processing"
        )
