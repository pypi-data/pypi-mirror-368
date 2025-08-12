from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.failure_prompt_response import FailurePromptResponse


class FailureExample(AbstractResponseExample):

    def example_class(self, indentation: Optional[int] = None):
        return FailurePromptResponse.create_failure(
            'Test failure message',
            context=self.io_manager.create_context(indentation=indentation)
        )

    def example_manager(self):
        self.io_manager.failure('Test failure message')

    def example_context(self):
        self.class_with_context.failure('Test failure message')
