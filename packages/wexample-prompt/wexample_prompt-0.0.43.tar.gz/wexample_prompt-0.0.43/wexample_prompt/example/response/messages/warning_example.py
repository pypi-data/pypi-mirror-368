from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.warning_prompt_response import WarningPromptResponse


class WarningExample(AbstractResponseExample):

    def example_class(self, indentation: Optional[int] = None):
        return WarningPromptResponse.create_warning(
            'Test warning message',
            context=self.io_manager.create_context(indentation=indentation)
        )

    def example_manager(self):
        self.io_manager.warning('Test warning message')

    def example_context(self):
        self.class_with_context.warning('Test warning message')
