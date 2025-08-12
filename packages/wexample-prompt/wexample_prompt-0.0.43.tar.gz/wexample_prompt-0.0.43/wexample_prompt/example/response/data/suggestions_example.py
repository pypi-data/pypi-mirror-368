"""Example for suggestions response."""
from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.data.suggestions_prompt_response import SuggestionsPromptResponse


class SuggestionsExample(AbstractResponseExample):
    """Example for suggestions response."""

    def get_example(self) -> str:
        message = "Here are some useful commands"
        suggestions = [
            "command1 --arg value",
            "command2",
            "command3 --flag"
        ]
        response = SuggestionsPromptResponse.create_suggestions(
            message=message,
            suggestions=suggestions,
            context=self.io_manager.create_context()
        )
        return response.render()

    def example_class(self, indentation: Optional[int] = None):
        """Example using class with context."""
        message = "Here are some useful commands"
        suggestions = [
            "command1 --arg value",
            "command2",
            "command3 --flag"
        ]
        context = self.io_manager.create_context()
        if indentation is not None:
            context.indentation = indentation
        return SuggestionsPromptResponse.create_suggestions(
            message=message,
            suggestions=suggestions,
            context=context
        )

    def example_manager(self):
        """Example using IoManager directly."""
        message = "Here are some useful commands"
        suggestions = [
            "command1 --arg value",
            "command2",
            "command3 --flag"
        ]
        self.io_manager.suggestions(
            message=message,
            suggestions=suggestions
        )

    def example_context(self):
        """Example using context."""
        message = "Here are some useful commands"
        suggestions = [
            "command1 --arg value",
            "command2",
            "command3 --flag"
        ]
        self.class_with_context.suggestions(
            message=message,
            suggestions=suggestions
        )
