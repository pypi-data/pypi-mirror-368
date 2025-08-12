from abc import abstractmethod
from typing import Optional, ClassVar, Tuple

from wexample_prompt.common.color_manager import ColorManager
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.responses.base_prompt_response import BasePromptResponse


class BaseMessageResponse(BasePromptResponse):
    # Symbol to display before the message, override in subclasses
    SYMBOL: ClassVar[str] = ""

    @classmethod
    @abstractmethod
    def get_message_type(cls) -> MessageType:
        pass

    @classmethod
    def _create_symbol_message(
            cls,
            text: str,
            color: TerminalColor,
            symbol: Optional[Tuple[str, False]] = None,
            bold_symbol: bool = True,
            context: Optional[PromptContext] = None,
            **kwargs
    ) -> 'BaseMessageResponse':
        """Create a message with a symbol.

        Args:
            text: Message text
            color: Text color
            symbol: Optional symbol to use instead of class symbol
            bold_symbol: Whether to make the symbol bold
            context: Optional prompt context
            **kwargs: Additional keyword arguments

        Returns:
            BaseMessageResponse: A new message response
        """
        segments = []

        # Add symbol if present
        if symbol or (symbol is None and cls.SYMBOL):
            symbol_text = f"{symbol or cls.SYMBOL} "
            symbol_segment = PromptResponseSegment(
                text=ColorManager.colorize(
                    symbol_text,
                    color,
                    TerminalColor.BOLD if bold_symbol else None
                )
            )
            segments.append(symbol_segment)

        # Add message text
        message = PromptResponseSegment(
            text=ColorManager.colorize(text, color)
        )
        segments.append(message)

        # Create line with segments
        line = PromptResponseLine(
            segments=segments,
            line_type=cls.get_message_type()
        )

        # Create response with context and additional kwargs
        create_args = {"lines": [line], "message_type": cls.get_message_type()}
        if context is not None:
            if "params" in kwargs:
                context.params = kwargs.pop("params")
            create_args["context"] = context
        create_args.update(kwargs)

        return cls._create(**create_args)
