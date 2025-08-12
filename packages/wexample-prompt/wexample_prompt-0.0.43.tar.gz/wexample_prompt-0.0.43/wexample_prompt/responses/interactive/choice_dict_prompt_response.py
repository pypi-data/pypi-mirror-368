"""Response for displaying and handling dictionary-based choice prompts."""
from typing import Any, Dict, Optional, List, Union, Type, TYPE_CHECKING

from InquirerPy.base.control import Choice
from pydantic import Field, ConfigDict

from wexample_prompt.responses.interactive.choice_prompt_response import ChoicePromptResponse
from wexample_prompt.common.prompt_context import PromptContext

if TYPE_CHECKING:
    from wexample_prompt.example.abstract_response_example import AbstractResponseExample


class ChoiceDictPromptResponse(ChoicePromptResponse):
    """Response for displaying choices from a dictionary and returning the selected key."""

    # Store the original dictionary for key lookup
    original_choices: Dict[str, str] = Field(default_factory=dict)

    # Pydantic configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def create_choice_dict(
        cls,
        question: str,
        choices: Dict[str, str],
        context: Optional[PromptContext] = None,
        default: Optional[str] = None,
        abort: Optional[str] = "> Abort",
        **kwargs: Any
    ) -> 'ChoiceDictPromptResponse':
        """Create a dictionary-based choice prompt response.
        
        Args:
            question: The question to display
            choices: Dictionary of choices (key: internal value, value: display text)
            context: Optional prompt context for formatting
            default: Optional default key
            abort: Optional abort choice text (None to disable)
            **kwargs: Additional arguments for inquirer.select
            
        Returns:
            ChoiceDictPromptResponse: A new dictionary choice prompt response
        """
        # Convert dictionary values to Choice objects
        choice_list: List[Union[str, Choice]] = []
        for key, value in choices.items():
            choice_list.append(Choice(value=key, name=value))

        # Create response with converted choices
        response = super().create_choice(
            question=question,
            choices=choice_list,
            context=context,
            default=default,
            abort=abort,
            **kwargs
        )
        response.original_choices = choices
        return response

    @classmethod
    def get_example_class(cls) -> Type["AbstractResponseExample"]:
        """Get the example class for dictionary choice prompts."""
        from wexample_prompt.example.response.interactive.choice_dict_example import ChoiceDictExample
        return ChoiceDictExample
