"""Mixin for handling suggestions responses in IoManager."""
from typing import List, Optional, TYPE_CHECKING

from wexample_prompt.enums.verbosity_level import VerbosityLevel

if TYPE_CHECKING:
    from wexample_prompt.responses.data.suggestions_prompt_response import SuggestionsPromptResponse


class SuggestionsPromptResponseManagerMixin:
    """Mixin for IoManager to handle suggestions responses."""

    def suggestions(
        self,
        message: str,
        suggestions: List[str],
        arrow_style: str = "→",
        verbosity: Optional[VerbosityLevel] = None,
        **kwargs
    ) -> "SuggestionsPromptResponse":
        """Create and display a suggestions response.

        Args:
            message: The message to display above suggestions
            suggestions: List of suggestion strings to display
            arrow_style: Character to use as bullet point (default: →)
            verbosity: Optional verbosity level for output detail
            **kwargs: Additional arguments passed to create_suggestions
        """
        from wexample_prompt.responses.data.suggestions_prompt_response import SuggestionsPromptResponse

        response = SuggestionsPromptResponse.create_suggestions(
            message=message,
            suggestions=suggestions,
            arrow_style=arrow_style,
            verbosity=verbosity,
            context=self.create_context(),
            **kwargs
        )

        self.print_response(response)
        return response
