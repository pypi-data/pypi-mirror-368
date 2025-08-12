"""Mixin for managing choice dict prompt responses."""
from typing import Any, Dict, Optional

from wexample_prompt.responses.interactive.choice_dict_prompt_response import ChoiceDictPromptResponse


class ChoiceDictPromptResponseManagerMixin:
    """Mixin class for managing choice dict prompt responses."""

    def choice_dict(
        self,
        question: str,
        choices: Dict[str, str],
        default: Optional[str] = None,
        abort: Optional[str] = "> Abort",
        **kwargs
    ) -> ChoiceDictPromptResponse:
        from wexample_prompt.responses.interactive import ChoiceDictPromptResponse

        response = ChoiceDictPromptResponse.create_choice_dict(
            question=question,
            choices=choices,
            context=self.create_context(),
            default=default,
            abort=abort,
            **kwargs
        )

        self.print_response(response)
        return response
