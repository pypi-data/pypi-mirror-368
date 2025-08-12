"""Response for displaying and handling choice prompts."""
from typing import Any, List, Optional, Dict, Union, Type, TYPE_CHECKING

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.utils import InquirerPyDefault, InquirerPySessionResult
from pydantic import Field, ConfigDict

from wexample_prompt.common.color_manager import ColorManager
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.enums.text_style import TextStyle
from wexample_prompt.responses.interactive.abstract_interactive_prompt_response import AbstractInteractivePromptResponse

if TYPE_CHECKING:
    from wexample_prompt.example.abstract_response_example import AbstractResponseExample


class ChoicePromptResponse(AbstractInteractivePromptResponse):
    """Response for displaying a list of choices and getting user selection."""

    # Instance variables
    choices: List[Union[str, Choice]] = Field(default_factory=list)
    default: Optional["InquirerPyDefault"] = None
    inquirer_kwargs: Dict[str, Any] = Field(default_factory=dict)
    question_text: str = Field(default="")  # Stockage du texte original de la question

    # Pydantic configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def create_choice(
        cls,
        question: str,
        choices: List[Any],
        context: Optional[PromptContext] = None,
        default: Optional["InquirerPyDefault"] = None,
        abort: Optional[str] = "> Abort",
        color: Optional[TerminalColor] = None,
        **kwargs: Any
    ) -> 'ChoicePromptResponse':
        lines = []

        # Add the question line with specified color (or blue as default) and bold style
        color = color or TerminalColor.BLUE
        lines.append(
            PromptResponseLine(segments=[
                PromptResponseSegment(
                    text=ColorManager.colorize(question, color),
                    styles=[TextStyle.BOLD]
                )
            ])
        )

        # Add each choice with a modern arrow and styling
        choices_all = choices.copy()
        if abort:
            choices_all.append(Choice(value=None, name=abort))

        for i, choice in enumerate(choices_all):
            # Handle both simple values and Choice objects
            choice_text = choice.name if isinstance(choice, Choice) else str(choice)

            lines.append(
                PromptResponseLine(segments=[
                    # Arrow indicator with cyan color
                    PromptResponseSegment(
                        text=ColorManager.colorize(f"  {i + 1}. → ", TerminalColor.CYAN)
                    ),
                    # Choice text with gray color and dim style
                    PromptResponseSegment(
                        text=ColorManager.colorize(choice_text, TerminalColor.WHITE),
                        styles=[TextStyle.DIM]
                    )
                ])
            )

        # Create default context if none provided
        if context is None:
            context = PromptContext()

        return cls(
            lines=lines,
            context=context,
            choices=choices_all,
            default=default,
            inquirer_kwargs=kwargs,
            question_text=question  # Stocker le texte original
        )

    def execute(self) -> "InquirerPySessionResult":
        """Execute the choice prompt and get user selection."""
        return inquirer.select(
            message=self.question_text,
            choices=self.choices,
            default=self.default,
            **self.inquirer_kwargs
        ).execute()

    @classmethod
    def get_example_class(cls) -> Type["AbstractResponseExample"]:
        """Get the example class for choice prompts."""
        from wexample_prompt.example.response.interactive.choice_example import ChoiceExample
        return ChoiceExample
