"""Tree response implementation."""
from typing import Dict, Any, Optional, List, Type, TYPE_CHECKING

from wexample_prompt.responses.base_prompt_response import BasePromptResponse
from wexample_prompt.enums.response_type import ResponseType
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.common.prompt_context import PromptContext

if TYPE_CHECKING:
    from wexample_prompt.example.abstract_response_example import AbstractResponseExample


class TreePromptResponse(BasePromptResponse):
    """Response for displaying hierarchical data in a tree structure."""

    # Instance variables
    data: Dict[str, Any]
    branch_style: str = "├"
    leaf_style: str = "└"
    pipe_style: str = "│"
    dash_style: str = "──"

    @classmethod
    def get_example_class(cls) -> Type["AbstractResponseExample"]:
        """Get the example class for this response type."""
        from wexample_prompt.example.response.data.tree_example import TreeExample

        return TreeExample

    @classmethod
    def create_tree(
        cls,
        data: Dict[str, Any],
        context: Optional[PromptContext] = None,
        **kwargs
    ) -> 'TreePromptResponse':
        """Create a tree response.

        Args:
            data: Dictionary of hierarchical data to display
            context: Optional prompt context for formatting
            **kwargs: Additional arguments passed to the constructor

        Returns:
            TreePromptResponse instance
        """
        return cls(
            lines=[],  # Lines will be generated in render()
            response_type=ResponseType.TREE,
            data=data,
            context=context,
            **kwargs
        )

    def render(self) -> str:
        """Render the tree structure."""
        if not self.data:
            return ""
            
        lines = []

        # Add empty line at the start
        lines.append(PromptResponseLine(segments=[PromptResponseSegment(text="")]))

        # Build tree structure
        self._build_tree(self.data, "", lines)

        # Add empty line at the end
        lines.append(PromptResponseLine(segments=[PromptResponseSegment(text="")]))
        
        # Update lines and render using parent class
        self.lines = lines
        return super().render()
    
    def _build_tree(self, data: Dict[str, Any], prefix: str, lines: List[PromptResponseLine]) -> None:
        """Recursively build tree structure.
        
        Args:
            data: Dictionary of current level data
            prefix: Current line prefix for indentation
            lines: List to append formatted lines to
        """
        items = list(data.items())
        for i, (key, value) in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = f"{self.leaf_style}{self.dash_style} " if is_last else f"{self.branch_style}{self.dash_style} "
            
            # Add current node
            segments = [PromptResponseSegment(text=f"{prefix}{current_prefix}{key}")]
            lines.append(PromptResponseLine(segments=segments))
            
            # Process children
            if isinstance(value, dict):
                next_prefix = prefix + ("    " if is_last else f"{self.pipe_style}   ")
                self._build_tree(value, next_prefix, lines)
            elif value is not None:
                next_prefix = prefix + ("    " if is_last else f"{self.pipe_style}   ")
                segments = [PromptResponseSegment(text=f"{next_prefix}{self.leaf_style}{self.dash_style} {value}")]
                lines.append(PromptResponseLine(segments=segments))
