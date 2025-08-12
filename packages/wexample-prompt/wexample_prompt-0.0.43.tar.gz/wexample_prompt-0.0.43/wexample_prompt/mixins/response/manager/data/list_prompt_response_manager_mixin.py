"""Mixin for managing list prompt responses."""
from typing import List, Optional, Any

from wexample_prompt.responses.data.list_prompt_response import ListPromptResponse


class ListPromptResponseManagerMixin:
    """Mixin class for managing list prompt responses."""

    def list(
        self,
        items: List[str],
        bullet: str = "•",
        **kwargs: Any
    ) -> ListPromptResponse:
        """Create a list response.

        Args:
            items: List of items to display
            bullet: Bullet character to use (default: •)
            **kwargs: Additional arguments passed to create_list

        Returns:
            ListPromptResponse: A new list response
        """
        response = ListPromptResponse.create_list(
            items=items,
            bullet=bullet,
            context=self.create_context(),
            **kwargs
        )
        self.print_response(response)
        return response
