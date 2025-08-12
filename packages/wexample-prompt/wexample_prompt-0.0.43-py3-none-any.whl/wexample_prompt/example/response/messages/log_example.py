from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.log_prompt_response import LogPromptResponse


class LogExample(AbstractResponseExample):

    def example_class(self, indentation: Optional[int] = None):
        return LogPromptResponse.create_log(
            'Test log message',
            context=self.io_manager.create_context(indentation=indentation),
            indentation=indentation
        )

    def example_manager(self):
        self.io_manager.log('Test log message')

    def example_context(self):
        self.class_with_context.log('Test log message')
