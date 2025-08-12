"""Base class for title responses."""
from abc import abstractmethod
from typing import Optional, TYPE_CHECKING

from wexample_prompt.common.color_manager import ColorManager
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.enums.response_type import ResponseType
from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.responses.base_prompt_response import BasePromptResponse

if TYPE_CHECKING:
    from wexample_prompt.common.prompt_context import PromptContext


class AbstractTitleResponse(BasePromptResponse):
    """Abstract base class for title responses."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._title_text = ""
        self._title_color = None
        self._fill_char = None

    @classmethod
    def _create_title(
        cls,
        text: str,
        context: "PromptContext",
        color: Optional[TerminalColor] = TerminalColor.CYAN,
        fill_char: Optional[str] = None,
        **kwargs
    ) -> 'AbstractTitleResponse':
        """Create a title response.
        
        Args:
            text (str): The title text
            color (Optional[TerminalColor]): Color for the title
            fill_char (str): Character to use for filling the line
            
        Returns:
            AbstractTitleResponse: A new title response
        """
        instance = cls(
            lines=[],  # Lines will be generated in render()
            response_type=ResponseType.TITLE,
            message_type=MessageType.LOG,
            context=context,
            **kwargs
        )

        instance._title_text = text
        instance._title_color = color
        instance._fill_char = fill_char or "⫻"

        return instance

    def render(self) -> str:
        """Render the title with current context dimensions."""
        # Get terminal width from context or default
        term_width = (
            self.context.get_effective_width()
            if self.context and hasattr(self.context, 'terminal_width')
            else 80
        )

        # Get indentation level
        indentation_level = (
            self.context.indentation
            if self.context and hasattr(self.context, 'indentation')
            else 0
        )

        # Calculate effective width (terminal width minus indentation)
        effective_width = term_width - (indentation_level * 2)

        # Get the prefix and text with padding
        prefix = self.get_prefix()
        text_with_padding = f" {self._title_text} "

        # Calculate remaining width for fill characters
        remaining_width = effective_width - len(prefix) - len(text_with_padding)
        fill_text = self._fill_char * max(0, remaining_width)

        # Combine all parts
        full_text = f"{prefix}{text_with_padding}{fill_text}"

        # Create colored segment
        title_segment = PromptResponseSegment(
            text=ColorManager.colorize(full_text, self._title_color)
            if self._title_color
            else full_text
        )

        # Create lines
        empty_line = PromptResponseLine(segments=[PromptResponseSegment(text="")])
        title_line = PromptResponseLine(segments=[title_segment])

        # Update lines
        self.lines = [empty_line, title_line, empty_line]

        # Call parent render
        return super().render()

    @classmethod
    @abstractmethod
    def get_prefix(cls) -> str:
        """Get the prefix for this title type.
        
        Returns:
            str: The prefix to use for this title type
        """
        pass
