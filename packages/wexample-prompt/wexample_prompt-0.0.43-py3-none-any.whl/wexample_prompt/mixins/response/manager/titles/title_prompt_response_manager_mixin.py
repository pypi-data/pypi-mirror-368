from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_prompt.responses.titles.title_prompt_response import TitlePromptResponse


class TitlePromptResponseManagerMixin:
    """Mixin for IoManager to handle title responses."""

    def title(self, message: str, **kwargs) -> "TitlePromptResponse":
        from wexample_prompt.responses.titles.title_prompt_response import TitlePromptResponse

        """Create and display a title response."""
        response = TitlePromptResponse.create_title(
            text=message,
            context=self.create_context(),
        )

        self.print_response(response)
        return response
