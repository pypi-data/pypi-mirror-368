"""Prompt response line implementation."""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.common.prompt_layout import PromptLayout


class PromptResponseLine(BaseModel):
    """A line of text composed of one or more segments with optional styling and layout."""
    
    segments: List[PromptResponseSegment] = Field(default_factory=list)
    line_type: Optional[MessageType] = None
    indent_level: int = Field(default=0, ge=0)
    layout: Optional[PromptLayout] = Field(default_factory=PromptLayout)

    @field_validator('segments')
    @classmethod
    def validate_segments(cls, v: List[PromptResponseSegment]) -> List[PromptResponseSegment]:
        """Ensure there is at least one segment.
        
        Args:
            v: List of segments to validate
            
        Returns:
            Validated list of segments
            
        Raises:
            ValueError: If no segments provided
        """
        if not v:
            raise ValueError("Line must have at least one segment")
        return v

    def combine(self, other: 'PromptResponseLine') -> 'PromptResponseLine':
        """Combine this line with another, preserving layout and type if possible."""
        return PromptResponseLine(
            segments=self.segments + other.segments,
            line_type=self.line_type or other.line_type,
            indent_level=max(self.indent_level, other.indent_level),
            layout=self.layout or other.layout
        )
    
    def render(self, context: PromptContext) -> str:
        """Render the line with all its segments.
        
        Args:
            context: Optional rendering context
            
        Returns:
            Rendered line as string
        """

        # Render all segments
        rendered_segments = [seg.render(context) for seg in self.segments]
        result = "".join(rendered_segments)
        
        # Apply message type color if present and colors are enabled
        if self.line_type and context.should_use_color():
            from wexample_prompt.common.color_manager import ColorManager
            color = ColorManager.get_message_color(self.line_type)
            result = ColorManager.colorize(result, color)
        
        # Apply indentation
        if self.indent_level > 0:
            result = "  " * self.indent_level + result
            
        return result
    
    def __str__(self) -> str:
        """Convert line to string, ignoring styling."""
        return "".join(segment.text for segment in self.segments)
