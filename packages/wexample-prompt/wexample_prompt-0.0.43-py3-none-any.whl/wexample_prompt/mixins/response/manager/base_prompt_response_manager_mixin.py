"""Mixin for base prompt response."""
from typing import TYPE_CHECKING, List, Optional, Dict, Any, Union

from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.enums.response_type import ResponseType
from wexample_prompt.responses.base_prompt_response import BasePromptResponse

if TYPE_CHECKING:
    from wexample_prompt.common.prompt_response_line import PromptResponseLine


class BasePromptResponseManagerMixin:
    """Mixin for base prompt response."""

    def base(
        self,
        message: Union[str, List["PromptResponseLine"]],
        response_type: ResponseType = ResponseType.PLAIN,
        message_type: MessageType = MessageType.LOG,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> BasePromptResponse:
        """Create a base prompt response.

        Args:
            message: String message or list of response lines
            response_type: Response type
            message_type: Message type
            metadata: Optional metadata
            **kwargs: Additional keyword arguments

        Returns:
            BasePromptResponse: A new base prompt response
        """
        from wexample_prompt.common.prompt_response_line import PromptResponseLine
        from wexample_prompt.common.prompt_response_segment import PromptResponseSegment

        if isinstance(message, str):
            lines = [
                PromptResponseLine(segments=[
                    PromptResponseSegment(text=message)
                ])
            ]
        else:
            lines = message

        response = BasePromptResponse.create_base(
            lines=lines,
            context=self.create_context(),
            response_type=response_type,
            message_type=message_type,
            metadata=metadata,
            **kwargs
        )

        self.print_response(response)
        return response

