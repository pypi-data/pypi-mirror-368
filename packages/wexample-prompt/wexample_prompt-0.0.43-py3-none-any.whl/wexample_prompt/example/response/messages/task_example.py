from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.task_prompt_response import TaskPromptResponse


class TaskExample(AbstractResponseExample):

    def example_class(self, indentation: Optional[int] = None):
        return TaskPromptResponse.create_task(
            'Test task message',
            context=self.io_manager.create_context(indentation=indentation)
        )

    def example_manager(self):
        self.io_manager.task('Test task message')

    def example_context(self):
        self.class_with_context.task('Test task message')
