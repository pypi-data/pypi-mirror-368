"""Mixin for success prompt responses."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse


class SuccessPromptResponseManagerMixin:
    """Mixin for success prompt responses."""

    def success(self, message: str) -> "AbstractPromptResponse":
        from wexample_prompt.responses.messages.success_prompt_response import SuccessPromptResponse

        """Create a success message."""
        response = SuccessPromptResponse.create_success(
            message=message,
            context=self.create_context(),
        )

        self.print_response(response)
        return response
