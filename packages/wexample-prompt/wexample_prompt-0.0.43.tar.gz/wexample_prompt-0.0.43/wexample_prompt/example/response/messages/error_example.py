from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.error_prompt_response import ErrorPromptResponse
from wexample_prompt.common.error_context import ErrorContext


class ErrorExample(AbstractResponseExample):

    def example_class(self, indentation: Optional[int] = None):
        context = self.io_manager.create_context(indentation=indentation)
        error_context = ErrorContext(**context.model_dump())
        return ErrorPromptResponse.create_error(
            'Test error message',
            context=error_context
        )

    def example_manager(self):
        self.io_manager.error('Test error message')

    def example_context(self):
        self.class_with_context.error('Test error message')
