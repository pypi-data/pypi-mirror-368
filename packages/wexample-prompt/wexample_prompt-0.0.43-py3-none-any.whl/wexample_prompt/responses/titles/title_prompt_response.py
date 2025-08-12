"""Title response implementation."""
from typing import Optional, TYPE_CHECKING, ClassVar, Type

from wexample_prompt.responses.titles.abstract_title_response import AbstractTitleResponse

if TYPE_CHECKING:
    from wexample_prompt.enums.terminal_color import TerminalColor
    from wexample_prompt.common.prompt_context import PromptContext
    from wexample_prompt.example.abstract_response_example import AbstractResponseExample


class TitlePromptResponse(AbstractTitleResponse):
    """Response for main titles with arrow prefix."""

    TITLE_CHAR: ClassVar[str] = "="

    @classmethod
    def get_example_class(cls) -> Type["AbstractResponseExample"]:
        from wexample_prompt.example.response.titles.title_example import TitleExample

        return TitleExample

    @classmethod
    def create_title(
        cls,
        text: str,
        context: "PromptContext",
        color: Optional["TerminalColor"] = None,
        fill_char: Optional[str] = None,
        **kwargs
    ) -> 'TitlePromptResponse':
        from wexample_prompt.enums.terminal_color import TerminalColor

        return super()._create_title(
            text=text,
            context=context,
            color=color or TerminalColor.CYAN,
            fill_char=fill_char,
            **kwargs
        )

    @classmethod
    def get_prefix(cls) -> str:
        return "❯"
