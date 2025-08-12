from typing import Dict, Any, Optional, List, ClassVar, Type, TYPE_CHECKING

from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.enums.response_type import ResponseType
from wexample_prompt.responses.base_prompt_response import BasePromptResponse

if TYPE_CHECKING:
    from wexample_prompt.example.abstract_response_example import AbstractResponseExample


class PropertiesPromptResponse(BasePromptResponse):
    properties: Dict[str, Any]
    title: Optional[str] = None
    nested_indent: int = 2

    @classmethod
    def get_example_class(cls) -> Type["AbstractResponseExample"]:
        from wexample_prompt.example.response.data.properties_example import PropertiesExample

        return PropertiesExample

    @classmethod
    def create_properties(
        cls,
        properties: Dict[str, Any],
        title: Optional[str] = None,
        nested_indent: int = 2,
        context: Optional[PromptContext] = None,
        **kwargs
    ) -> 'PropertiesPromptResponse':
        return cls(
            lines=[],  # Lines will be generated in render()
            response_type=ResponseType.PROPERTIES,
            properties=properties,
            title=title,
            nested_indent=nested_indent,
            context=context,
            **kwargs
        )

    def render(self) -> str:
        """Render the properties in a formatted box."""
        if not self.properties:
            return ""

        # Calculate total width including padding
        total_width = self.context.get_effective_width() if self.context else 80
        # Content width is total minus padding (2)
        content_width = total_width - 2

        # Calculate the maximum width needed for content
        max_key_width = max(len(str(key)) for key in self.properties.keys())
        content_lines = self._format_properties(self.properties, max_key_width, self.nested_indent)

        # Empty line at start
        lines = [PromptResponseLine(segments=[PromptResponseSegment(text="")])]

        # Add title if provided
        if self.title:
            title_padding = (content_width - len(self.title)) // 2
            title_line = PromptResponseLine(segments=[
                PromptResponseSegment(text="-" * title_padding),
                PromptResponseSegment(text=f" {self.title} "),
                PromptResponseSegment(text="-" * (content_width - title_padding - len(self.title) - 2))
            ])
            lines.append(title_line)
        else:
            # Top border
            lines.append(self._create_border_line(content_width))

        # Add content lines
        for content in content_lines:
            lines.append(PromptResponseLine(segments=[
                PromptResponseSegment(text=" "),
                PromptResponseSegment(text=content)
            ]))

        # Bottom border
        lines.append(self._create_border_line(content_width))

        # Update lines and render using parent class
        self.lines = lines
        return super().render()

    @staticmethod
    def _format_properties(
        properties: Dict[str, Any],
        key_width: int,
        indent: int,
        current_indent: int = 0
    ) -> List[str]:
        lines = []
        indent_str = " " * current_indent

        for key, value in properties.items():
            if isinstance(value, dict):
                lines.append(f"{indent_str}{str(key)}:")
                lines.extend(PropertiesPromptResponse._format_properties(
                    value, key_width, indent, current_indent + indent
                ))
            else:
                key_str = str(key).ljust(key_width)
                lines.append(f"{indent_str}{key_str} : {str(value)}")

        return lines

    @staticmethod
    def _create_border_line(width: int, left: str = "", right: str = "") -> PromptResponseLine:
        from wexample_prompt.const.formatting import INDENTATION_SPACES

        return PromptResponseLine(segments=[
            PromptResponseSegment(text=f"{left}{'-' * width}{right}")
        ])
