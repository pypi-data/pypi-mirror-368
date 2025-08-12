from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_prompt.responses.messages import DebugPromptResponse


class DebugPromptResponseManagerMixin:
    """Mixin for IoManager to handle debug responses."""

    def debug(self, message: str, **kwargs) -> "DebugPromptResponse":
        from wexample_prompt.responses.messages import DebugPromptResponse

        """Create and display a debug response."""
        response = DebugPromptResponse.create_debug(
            message=message,
            context=self.create_context(),
        )

        if self._logger.handlers:
            self._logger.debug(message)

        self.print_response(response)
        return response
