from typing import ClassVar, Type, TYPE_CHECKING, Optional

from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.responses.messages.base_message_response import BaseMessageResponse
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.common.prompt_context import PromptContext

if TYPE_CHECKING:
    from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
    from wexample_prompt.example.abstract_response_example import AbstractResponseExample


class FailurePromptResponse(BaseMessageResponse):
    """Response for failure messages."""
    
    SYMBOL: ClassVar[str] = "❌"
    
    @classmethod
    def create_failure(
        cls: "FailurePromptResponse",
        message: str,
        context: PromptContext = None,
        color: Optional[TerminalColor] = None,
        **kwargs
    ) -> "AbstractPromptResponse":
        return cls._create_symbol_message(
            text=message,
            context=context,
            color=color or TerminalColor.RED,
            **kwargs
        )
    
    @classmethod
    def get_message_type(cls) -> MessageType:
        """Get the message type for failure messages."""
        return MessageType.FAILURE

    @classmethod
    def get_example_class(cls) -> Type["AbstractResponseExample"]:
        """Get the example class for failure messages."""
        from wexample_prompt.example.response.messages.failure_example import FailureExample
        return FailureExample
