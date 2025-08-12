"""A response that contains multiple responses of different types."""
from typing import List, Optional

from pydantic import Field

from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.responses.base_prompt_response import BasePromptResponse
from wexample_prompt.enums.response_type import ResponseType
from wexample_prompt.enums.message_type import MessageType


class MultiplePromptResponse(BasePromptResponse):
    """A response that contains multiple responses of different types.
    
    This class allows grouping multiple prompt responses of different types into a single
    response object. The responses are rendered and printed in sequence.

    Attributes:
        responses: List of prompt responses to be rendered together
        lines: List of lines to be rendered together
        response_type: Type of the response (always MULTIPLE)
        message_type: Type of message (always LOG)
    """

    responses: List[AbstractPromptResponse] = Field(
        default_factory=list,
        description="List of prompt responses to be rendered together"
    )
    lines: List[str] = Field(
        default_factory=list,
        description="List of lines to be rendered together"
    )
    response_type: ResponseType = Field(
        default=ResponseType.MULTIPLE,
        description="Type of the response (always MULTIPLE)"
    )
    message_type: MessageType = Field(
        default=MessageType.LOG,
        description="Type of message (always LOG)"
    )

    @classmethod
    def get_example_class(cls) -> type:
        """Get the example class for this response type.

        Returns:
            Type: The example class
        """
        from wexample_prompt.example.response.data.multiple_example import MultipleExample
        return MultipleExample

    @classmethod
    def multiple(cls, responses: List[AbstractPromptResponse], **kwargs) -> 'MultiplePromptResponse':
        """Create a multiple prompt response.

        Args:
            responses: List of responses to include
            **kwargs: Additional arguments passed to the constructor

        Returns:
            MultiplePromptResponse: A new multiple response instance
        """
        return cls.create_multiple(responses=responses, **kwargs)

    @classmethod
    def create_multiple(
        cls,
        responses: Optional[List[AbstractPromptResponse]] = None,
        **kwargs
    ) -> 'MultiplePromptResponse':
        """Create a new MultiplePromptResponse from a list of responses.
        
        Args:
            responses: List of responses to include, defaults to empty list
            **kwargs: Additional arguments to pass to the constructor
        
        Returns:
            MultiplePromptResponse: A new instance with the given responses
        """
        if responses is None:
            responses = []

        return cls(
            responses=responses,
            response_type=ResponseType.MULTIPLE,
            message_type=MessageType.LOG,
            **kwargs
        )

    def render(self) -> str:
        """Render all contained responses in sequence.
        
        Returns:
            str: The rendered string containing all responses
        """
        return "\n".join(response.render() for response in self.responses)

    def print(self, *args, **kwargs) -> None:
        """Print all contained responses in sequence.
        
        Args:
            *args: Positional arguments passed to each response's print method
            **kwargs: Keyword arguments passed to each response's print method
        """
        for response in self.responses:
            response.print(*args, **kwargs)

    @classmethod
    def create(cls, *args, **kwargs) -> 'MultiplePromptResponse':
        """Create a new MultiplePromptResponse instance.
        
        This is an alias for create_multiple to maintain consistency with other response classes.
        
        Args:
            *args: Arguments to pass to create_multiple
            **kwargs: Keyword arguments to pass to create_multiple
        
        Returns:
            MultiplePromptResponse: A new instance
        """
        return cls.create_multiple(*args, **kwargs)

    def append_response(self, response: AbstractPromptResponse) -> 'MultiplePromptResponse':
        """Add a new response to the list.
        
        Args:
            response: The response to append
        
        Returns:
            MultiplePromptResponse: Self for method chaining
        """
        self.responses.append(response)
        return self

    def extend_responses(self, responses: List[AbstractPromptResponse]) -> 'MultiplePromptResponse':
        """Add multiple responses to the list.
        
        Args:
            responses: List of responses to add
        
        Returns:
            MultiplePromptResponse: Self for method chaining
        """
        self.responses.extend(responses)
        return self
