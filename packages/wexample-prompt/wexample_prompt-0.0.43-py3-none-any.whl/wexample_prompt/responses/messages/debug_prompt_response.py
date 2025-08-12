from typing import ClassVar, Type, TYPE_CHECKING, Optional

from wexample_prompt.responses.messages.base_message_response import BaseMessageResponse

if TYPE_CHECKING:
    from wexample_prompt.enums.message_type import MessageType
    from wexample_prompt.common.prompt_context import PromptContext
    from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
    from wexample_prompt.example.abstract_response_example import AbstractResponseExample
    from wexample_prompt.enums.terminal_color import TerminalColor


class DebugPromptResponse(BaseMessageResponse):
    SYMBOL: ClassVar[str] = "🔍"

    @classmethod
    def create_debug(
        cls: "DebugPromptResponse",
        message: str,
        context: "PromptContext" = None,
        color: Optional["TerminalColor"] = None,
        **kwargs
    ) -> "AbstractPromptResponse":
        from wexample_prompt.enums.terminal_color import TerminalColor

        return cls._create_symbol_message(
            text=message,
            context=context,
            color=color or TerminalColor.CYAN
        )

    @classmethod
    def get_message_type(cls) -> "MessageType":
        from wexample_prompt.enums.message_type import MessageType

        return MessageType.DEBUG

    @classmethod
    def get_example_class(cls) -> Type["AbstractResponseExample"]:
        from wexample_prompt.example.response.messages.debug_example import DebugExample

        return DebugExample
