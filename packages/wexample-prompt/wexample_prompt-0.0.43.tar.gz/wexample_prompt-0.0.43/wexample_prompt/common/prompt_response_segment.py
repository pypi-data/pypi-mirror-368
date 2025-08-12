from typing import List, Optional
from pydantic import BaseModel

from wexample_prompt.enums.text_style import TextStyle


class PromptResponseSegment(BaseModel):
    """A segment of text with optional styling."""
    
    text: str
    styles: List[TextStyle] = []
    
    def combine(self, other: 'PromptResponseSegment') -> 'PromptResponseSegment':
        """Combine this segment with another, merging text and styles."""
        return PromptResponseSegment(
            text=self.text + other.text,
            styles=list(set(self.styles + other.styles))
        )
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PromptResponseSegment):
            return NotImplemented
        return self.text == other.text and set(self.styles) == set(other.styles)
    
    def apply_style(self, style: TextStyle) -> 'PromptResponseSegment':
        """Apply additional style to the segment."""
        return PromptResponseSegment(
            text=self.text,
            styles=list(set(self.styles + [style]))
        )
    
    def with_styles(self, additional_styles: List[TextStyle]) -> 'PromptResponseSegment':
        """Create a new segment with additional styles."""
        return PromptResponseSegment(
            text=self.text,
            styles=list(set(self.styles + additional_styles))
        )
    
    def render(self, context: 'PromptContext') -> str:
        """Render the segment with its styles."""
        from wexample_prompt.common.prompt_context import PromptContext
        
        result = self.text
        if not context.should_use_color():
            return result
            
        # Apply all style codes first
        style_codes = []
        for style in self.styles:
            code = self._get_ansi_code(style)
            if code:
                style_codes.append(code)
                
        # Only add styles if we have any
        if style_codes:
            result = f"{''.join(style_codes)}{result}\033[0m"
            
        return result
    
    @staticmethod
    def _get_ansi_code(style: TextStyle) -> str:
        """Get ANSI style code without reset."""
        style_codes = {
            TextStyle.BOLD: "\033[1m",
            TextStyle.ITALIC: "\033[3m",
            TextStyle.UNDERLINE: "\033[4m",
            TextStyle.STRIKETHROUGH: "\033[9m",
            TextStyle.DIM: "\033[2m",
            TextStyle.REVERSE: "\033[7m",
            TextStyle.HIDDEN: "\033[8m",
        }
        return style_codes.get(style, "")
