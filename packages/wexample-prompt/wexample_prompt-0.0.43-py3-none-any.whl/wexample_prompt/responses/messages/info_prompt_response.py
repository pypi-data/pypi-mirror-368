from typing import ClassVar, Type, TYPE_CHECKING, Optional

from wexample_prompt.responses.messages.base_message_response import BaseMessageResponse

if TYPE_CHECKING:
    from wexample_prompt.enums.message_type import MessageType
    from wexample_prompt.common.prompt_context import PromptContext
    from wexample_prompt.example.abstract_response_example import AbstractResponseExample
    from wexample_prompt.enums.terminal_color import TerminalColor


class InfoPromptResponse(BaseMessageResponse):
    """Response for info messages."""
    
    SYMBOL: ClassVar[str] = "ℹ"
    
    @classmethod
    def create_info(
        cls: "InfoPromptResponse",
        message: str,
        context: "PromptContext" = None,
        color: Optional["TerminalColor"] = None,
        **kwargs
    ) -> "InfoPromptResponse":
        from wexample_prompt.enums.terminal_color import TerminalColor

        return cls._create_symbol_message(
            text=message,
            context=context,
            color=color or TerminalColor.BLUE
        )

    @classmethod
    def get_message_type(cls) -> "MessageType":
        from wexample_prompt.enums.message_type import MessageType

        return MessageType.INFO

    @classmethod
    def get_example_class(cls) -> Type["AbstractResponseExample"]:
        """Get the example class for info messages."""
        from wexample_prompt.example.response.messages.info_example import InfoExample
        return InfoExample
