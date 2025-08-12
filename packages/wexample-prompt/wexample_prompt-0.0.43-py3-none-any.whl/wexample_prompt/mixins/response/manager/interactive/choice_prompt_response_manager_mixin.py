from typing import TYPE_CHECKING, Optional, List, Any

from InquirerPy.utils import InquirerPyDefault

if TYPE_CHECKING:
    from wexample_prompt.responses.interactive import ChoicePromptResponse


class ChoicePromptResponseManagerMixin:
    def choice(
        self,
        question: str,
        choices: List[Any],
        default: Optional[InquirerPyDefault] = None,
        abort: Optional[str] = "> Abort",
        **kwargs
    ) -> "ChoicePromptResponse":
        from wexample_prompt.responses.interactive import ChoicePromptResponse

        response = ChoicePromptResponse.create_choice(
            question=question,
            choices=choices,
            context=self.create_context(),
            default=default,
            abort=abort,
            **kwargs
        )

        self.print_response(response)
        return response
