"""Example usage of MultiplePromptResponse."""
from typing import List, Dict, Any, Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.data.list_prompt_response import ListPromptResponse
from wexample_prompt.responses.data.multiple_prompt_response import MultiplePromptResponse
from wexample_prompt.responses.messages.log_prompt_response import LogPromptResponse


class MultipleExample(AbstractResponseExample):
    """Example usage of MultiplePromptResponse."""

    def example_class(self, indentation: Optional[int] = None):
        """Example using the class directly."""
        responses = [
            LogPromptResponse.create_log("First response", context=self.io_manager.create_context()),
            ListPromptResponse.create_list(items=["Item 1", "Item 2"], context=self.io_manager.create_context()),
            LogPromptResponse.create_log("Last response", context=self.io_manager.create_context())
        ]
        return MultiplePromptResponse.create_multiple(
            responses=responses,
            context=self.io_manager.create_context(indentation=indentation)
        )

    def example_manager(self):
        """Example using the IoManager."""
        responses = [
            LogPromptResponse.create_log("First response", context=self.io_manager.create_context()),
            ListPromptResponse.create_list(items=["Item 1", "Item 2"], context=self.io_manager.create_context()),
            LogPromptResponse.create_log("Last response", context=self.io_manager.create_context())
        ]
        self.io_manager.multiple(responses=responses)

    def example_context(self):
        """Example using PromptContext."""
        responses = [
            LogPromptResponse.create_log("First response", context=self.io_manager.create_context()),
            ListPromptResponse.create_list(items=["Item 1", "Item 2"], context=self.io_manager.create_context()),
            LogPromptResponse.create_log("Last response", context=self.io_manager.create_context())
        ]
        self.class_with_context.multiple(responses=responses)

    def get_examples(self) -> List[Dict[str, Any]]:
        """Get list of examples.

        Returns:
            List[Dict[str, Any]]: List of example configurations
        """
        return [
            {
                "title": "Simple Multiple",
                "description": "Display multiple responses in sequence",
                "callback": self.simple_multiple
            },
            {
                "title": "Mixed Types",
                "description": "Display different types of responses together",
                "callback": self.mixed_types
            },
            {
                "title": "Dynamic Multiple",
                "description": "Build multiple responses dynamically",
                "callback": self.dynamic_multiple
            }
        ]

    def simple_multiple(self) -> Optional[MultiplePromptResponse]:
        """Show a simple multiple response example."""
        responses = [
            LogPromptResponse.create_log("First message", context=self.io_manager.create_context()),
            LogPromptResponse.create_log("Second message", context=self.io_manager.create_context()),
            LogPromptResponse.create_log("Third message", context=self.io_manager.create_context())
        ]
        return self.io_manager.multiple(responses=responses)

    def mixed_types(self) -> Optional[MultiplePromptResponse]:
        """Show different response types together."""
        responses = [
            LogPromptResponse.create_log("Log response", context=self.io_manager.create_context()),
            ListPromptResponse.create_list(
                items=["List item 1", "List item 2"],
                context=self.io_manager.create_context()
            ),
            LogPromptResponse.create_log("Another log response", context=self.io_manager.create_context())
        ]
        return self.io_manager.multiple(responses=responses)

    def dynamic_multiple(self) -> Optional[MultiplePromptResponse]:
        """Show building responses dynamically."""
        response = MultiplePromptResponse.create_multiple(
            responses=[LogPromptResponse.create_log("Initial response", context=self.io_manager.create_context())],
            context=self.io_manager.create_context()
        )

        # Add more responses
        response.append_response(
            ListPromptResponse.create_list(items=["Dynamic item 1"], context=self.io_manager.create_context())
        )
        response.extend_responses([
            LogPromptResponse.create_log("Added later", context=self.io_manager.create_context()),
            ListPromptResponse.create_list(items=["Dynamic item 2"], context=self.io_manager.create_context())
        ])

        return response
