from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type, TYPE_CHECKING

from pydantic import BaseModel, Field

from wexample_helpers.classes.mixin.has_snake_short_class_name_class_mixin import HasSnakeShortClassNameClassMixin
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.enums.response_type import ResponseType
from wexample_prompt.enums.text_style import TextStyle
from wexample_prompt.enums.verbosity_level import VerbosityLevel

if TYPE_CHECKING:
    from wexample_prompt.example.abstract_response_example import AbstractResponseExample


class AbstractPromptResponse(HasSnakeShortClassNameClassMixin, BaseModel, ABC):
    """Abstract base class for all prompt responses."""
    lines: List[PromptResponseLine]
    response_type: ResponseType = ResponseType.PLAIN
    metadata: Dict[str, Any] = Field(default_factory=dict)
    message_type: MessageType = MessageType.LOG
    context: PromptContext = Field(...)
    verbosity_level: Optional[VerbosityLevel] = Field(default=VerbosityLevel.DEFAULT)

    def __init__(self, **data):
        super().__init__(**data)

        # Validate the presence of the expected creation method
        self._validate_creation_method()

    @classmethod
    @abstractmethod
    def get_example_class(cls) -> Type["AbstractResponseExample"]:
        pass

    def _validate_creation_method(self):
        short_name = self.get_snake_short_class_name()
        expected_method_name = f"create_{short_name}"

        if not hasattr(self.__class__, expected_method_name):
            raise NotImplementedError(
                f"The method '{expected_method_name}' is not implemented in the class {self.__class__.__name__}. "
                "Ensure that this method is defined to handle this response type."
            )

    @classmethod
    def get_class_name_suffix(cls) -> Optional[str]:
        return "PromptResponse"

    def render(self) -> str:
        """Render the complete response."""
        # Check if this message should be shown based on verbosity
        if not self.context.should_show_message(self.verbosity_level):
            return ""

        rendered_lines = []
        indent = self.context.get_indentation()
        for line in self.lines:
            rendered = line.render(self.context)
            if rendered:  # Only indent non-empty lines
                rendered = indent + rendered
            rendered_lines.append(rendered)

        # Format message with parameters if any
        return self.context.format_message(
            "\n".join(rendered_lines)
        )

    @classmethod
    def _create(
        cls: "AbstractPromptResponse",
        lines: List[PromptResponseLine],
        context: PromptContext = None,
        **kwargs
    ) -> "AbstractPromptResponse":
        """Create a new response with the given lines."""
        return cls(lines=lines, context=context, **kwargs)

    def append(self, other: 'AbstractPromptResponse') -> 'AbstractPromptResponse':
        """Combine this response with another."""
        return self.__class__(
            lines=self.lines + other.lines,
            response_type=self.response_type,
            metadata={**self.metadata, **other.metadata},
            message_type=self.message_type,
            context=self.context
        )

    def wrap(self, styles: List[TextStyle]) -> 'AbstractPromptResponse':
        """Apply styles to all segments in all lines."""
        new_lines = []
        for line in self.lines:
            new_segments = [
                segment.with_styles(styles)
                for segment in line.segments
            ]
            new_lines.append(PromptResponseLine(
                segments=new_segments,
                line_type=line.line_type,
                indent_level=line.indent_level,
                layout=line.layout
            ))
        return self.__class__(
            lines=new_lines,
            response_type=self.response_type,
            metadata=self.metadata,
            message_type=self.message_type,
            context=self.context
        )
