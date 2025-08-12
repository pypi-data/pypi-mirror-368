from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_prompt.responses.messages import TaskPromptResponse


class TaskPromptResponseManagerMixin:
    def task(self, message: str, **kwargs) -> "TaskPromptResponse":
        from wexample_prompt.responses.messages import TaskPromptResponse

        response = TaskPromptResponse.create_task(
            message=message,
            context=self.create_context(),
        )

        self.print_response(response)
        return response
