"""Example for base prompt response."""
from typing import Type, TYPE_CHECKING, Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.base_prompt_response import BasePromptResponse

if TYPE_CHECKING:
    from wexample_prompt.common.io_manager import IoManager
    from wexample_prompt.example.example_class_with_context import ExampleClassWithContext


class BaseExample(AbstractResponseExample):
    """Example for base prompt response."""

    def get_test_message(self) -> str:
        """Get test message."""
        return "Test base message"

    def example_manager(self) -> "IoManager":
        """Get example manager."""
        from wexample_prompt.common.io_manager import IoManager

        return IoManager()

    def example_context(self) -> "ExampleClassWithContext":
        """Get example context."""
        from wexample_prompt.example.example_class_with_context import ExampleClassWithContext

        return ExampleClassWithContext()

    def example_class(self, indentation: Optional[int] = None) -> "BasePromptResponse":
        """Get example class."""
        from wexample_prompt.common.prompt_response_line import PromptResponseLine
        from wexample_prompt.common.prompt_response_segment import PromptResponseSegment

        return BasePromptResponse.create_base(
            lines=[
                PromptResponseLine(segments=[
                    PromptResponseSegment(text=self.get_test_message())
                ])
            ],
            context=self.io_manager.create_context(indentation=indentation),
            indentation=indentation
        )
