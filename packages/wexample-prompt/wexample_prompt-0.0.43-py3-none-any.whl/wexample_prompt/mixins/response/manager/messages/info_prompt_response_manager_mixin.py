from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_prompt.responses.messages import InfoPromptResponse


class InfoPromptResponseManagerMixin:
    def info(self, message: str, **kwargs) -> "InfoPromptResponse":
        from wexample_prompt.responses.messages import InfoPromptResponse

        response = InfoPromptResponse.create_info(
            message=message,
            context=self.create_context(),
        )

        if self._logger.handlers:
            self._logger.debug(message)

        self.print_response(response)
        return response
