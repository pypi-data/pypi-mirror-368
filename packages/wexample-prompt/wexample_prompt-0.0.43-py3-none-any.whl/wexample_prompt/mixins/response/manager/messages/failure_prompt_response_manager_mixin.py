from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_prompt.responses.messages import FailurePromptResponse


class FailurePromptResponseManagerMixin:
    def failure(self, message: str, **kwargs) -> "FailurePromptResponse":
        from wexample_prompt.responses.messages import FailurePromptResponse

        response = FailurePromptResponse.create_failure(
            message=message,
            context=self.create_context(),
        )

        self.print_response(response)
        return response
