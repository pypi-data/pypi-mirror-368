"""Mixin for handling tree responses in IoManager."""
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_prompt.responses.data.tree_prompt_response import TreePromptResponse


class TreePromptResponseManagerMixin:
    """Mixin for IoManager to handle tree responses."""

    def tree(
        self,
        data: Dict[str, Any],
        **kwargs
    ) -> "TreePromptResponse":
        """Create and display a tree response.

        Args:
            data: Dictionary of hierarchical data to display
            **kwargs: Additional arguments passed to create_tree

        Returns:
            TreePromptResponse instance
        """
        from wexample_prompt.responses.data.tree_prompt_response import TreePromptResponse

        response = TreePromptResponse.create_tree(
            data=data,
            context=self.create_context(),
            **kwargs
        )

        self.print_response(response)
        return response
