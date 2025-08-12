from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_prompt.responses.messages.log_prompt_response import LogPromptResponse
    from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse


class LogPromptResponseManagerMixin:
    def log(self, message: str) -> "AbstractPromptResponse":
        from wexample_prompt.responses.messages.log_prompt_response import LogPromptResponse

        response = LogPromptResponse.create_log(
            message=message,
            context=self.create_context(),
        )

        self.print_response(response)
        return response
