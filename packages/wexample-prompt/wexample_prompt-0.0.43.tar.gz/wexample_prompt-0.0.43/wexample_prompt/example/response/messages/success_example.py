"""Example for success prompt response."""
from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.success_prompt_response import SuccessPromptResponse


class SuccessExample(AbstractResponseExample):
    """Example class for success prompt response."""

    def example_class(self, indentation: Optional[int] = None):
        """Example using direct class method."""
        return SuccessPromptResponse.create_success(
            'Test success message',
            context=self.io_manager.create_context(indentation=indentation),
            indentation=indentation
        )

    def example_manager(self):
        """Example using IoManager."""
        self.io_manager.success('Test success message')

    def example_context(self):
        """Example using context."""
        self.class_with_context.success('Test success message')
