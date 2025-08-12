from typing import ClassVar, Type, TYPE_CHECKING, Optional

from wexample_prompt.common.error_context import ErrorContext
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.responses.messages.base_message_response import BaseMessageResponse

if TYPE_CHECKING:
    from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
    from wexample_prompt.example.abstract_response_example import AbstractResponseExample


class WarningPromptResponse(BaseMessageResponse):
    """Response for warning messages."""

    SYMBOL: ClassVar[str] = "⚠️"

    @classmethod
    def create_warning(
            cls: "WarningPromptResponse",
            message: str,
            context: ErrorContext = None,
            color: Optional[TerminalColor] = None,
            **kwargs
    ) -> "AbstractPromptResponse":
        return cls._create_symbol_message(
            text=message,
            context=context or ErrorContext(),
            color=color or TerminalColor.YELLOW,
            **kwargs
        )

    @classmethod
    def get_message_type(cls) -> MessageType:
        """Get the message type for warning messages."""
        return MessageType.WARNING

    @classmethod
    def get_example_class(cls) -> Type["AbstractResponseExample"]:
        """Get the example class for warning messages."""
        from wexample_prompt.example.response.messages.warning_example import WarningExample
        return WarningExample
