from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_prompt.responses.titles.subtitle_prompt_response import SubtitlePromptResponse


class SubtitlePromptResponseManagerMixin:
    """Mixin for IoManager to handle subtitle responses."""

    def subtitle(self, message: str, **kwargs) -> "SubtitlePromptResponse":
        from wexample_prompt.responses.titles.subtitle_prompt_response import SubtitlePromptResponse
        
        """Create and display a subtitle response."""
        response = SubtitlePromptResponse.create_subtitle(
            text=message,
            context=self.create_context(),
        )

        self.print_response(response)
        return response
