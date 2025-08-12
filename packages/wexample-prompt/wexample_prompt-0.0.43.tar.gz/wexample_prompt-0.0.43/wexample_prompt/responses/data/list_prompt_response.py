"""Response for displaying items in a bulleted list."""
from typing import List, Optional

from wexample_prompt.responses.base_prompt_response import BasePromptResponse
from wexample_prompt.enums.response_type import ResponseType
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.common.color_manager import ColorManager


class ListPromptResponse(BasePromptResponse):
    """Response for displaying items in a bulleted list."""

    items: List[str]
    bullet: str = "•"
    color: Optional[TerminalColor] = None

    @classmethod
    def get_example_class(cls) -> type:
        """Get the example class for this response type.

        Returns:
            Type: The example class
        """
        from wexample_prompt.example.response.data.list_example import ListExample
        return ListExample

    @classmethod
    def create_list(
        cls,
        items: List[str],
        bullet: str = "•",
        context: Optional[PromptContext] = None,
        color: Optional[TerminalColor] = None,
        **kwargs
    ) -> 'ListPromptResponse':
        """Create a list response.
        
        Args:
            items: List of items to display
            bullet: Bullet character to use (default: •)
            context: Optional prompt context for formatting
            color: Optional color for the list items
            **kwargs: Additional arguments
            
        Returns:
            ListPromptResponse: A new list response
        """
        # If color is specified, colorize each item
        if color:
            items = [ColorManager.colorize(item, color) for item in items]

        return cls(
            lines=[],  # Lines will be generated in render()
            response_type=ResponseType.LIST,
            items=items,
            bullet=bullet,
            color=color,
            context=context
        )

    def render(self) -> str:
        """Render the list with bullets and indentation."""
        if not self.items:
            return ""

        lines = []
        for item in self.items:
            # Check if this is a sub-item by looking for leading spaces
            indent_level = 0
            content = item
            
            while content.startswith("  "):
                indent_level += 1
                content = content[2:]
                
            # Remove bullet if the content already has one
            if content.startswith(f"{self.bullet} "):
                content = content[2:]

            # Create bullet segment with color if specified
            bullet_text = "  " * indent_level + f"{self.bullet} "
            if self.color:
                bullet_text = ColorManager.colorize(bullet_text, self.color)

            # Create line with proper indentation
            segments = [
                PromptResponseSegment(text=bullet_text),
                PromptResponseSegment(text=content)
            ]
            lines.append(PromptResponseLine(segments=segments))

        # Update lines and render
        self.lines = lines
        return super().render()
