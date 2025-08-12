from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_prompt.responses.messages import WarningPromptResponse


class WarningPromptResponseManagerMixin:
    def warning(self, message: str, **kwargs) -> "WarningPromptResponse":
        from wexample_prompt.responses.messages import WarningPromptResponse

        response = WarningPromptResponse.create_warning(
            message=message,
            context=self.create_context(),
            **kwargs
        )

        self.print_response(response)
        return response
