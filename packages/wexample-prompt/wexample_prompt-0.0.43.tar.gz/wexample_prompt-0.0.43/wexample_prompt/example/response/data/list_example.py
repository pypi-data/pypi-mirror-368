"""Example usage of ListPromptResponse."""
from typing import List, Any, Dict, Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.data.list_prompt_response import ListPromptResponse
from wexample_prompt.enums.terminal_color import TerminalColor


class ListExample(AbstractResponseExample):
    """Example usage of ListPromptResponse."""

    @classmethod
    def get_response_class(cls) -> type:
        """Get the response class this example is for.

        Returns:
            Type: The response class
        """
        return ListPromptResponse

    def get_examples(self) -> List[Dict[str, Any]]:
        """Get list of examples.

        Returns:
            List[Dict[str, Any]]: List of example configurations
        """
        return [
            {
                "title": "Simple List",
                "description": "Display a simple list of items",
                "callback": self.simple_list
            },
            {
                "title": "Nested List",
                "description": "Display a nested list with indentation",
                "callback": self.nested_list
            },
            {
                "title": "Colored List",
                "description": "Display a list with colored items",
                "callback": self.colored_list
            },
            {
                "title": "Custom Bullet",
                "description": "Display a list with custom bullet character",
                "callback": self.custom_bullet
            },
            {
                "title": "Example Class",
                "description": "Example using the class directly",
                "callback": self.example_class
            },
            {
                "title": "Example Manager",
                "description": "Example using the IoManager",
                "callback": self.example_manager
            },
            {
                "title": "Example Context",
                "description": "Example using PromptContext",
                "callback": self.example_context
            }
        ]

    def example_class(self, indentation: Optional[int] = None):
        """Example using the class directly."""
        items = [
            "First item",
            "Second item",
            "Third item"
        ]
        return ListPromptResponse.create_list(
            items=items,
            context=self.io_manager.create_context(indentation=indentation)
        )

    def example_manager(self):
        """Example using the IoManager."""
        items = [
            "First item",
            "Second item",
            "Third item"
        ]
        self.io_manager.list(items=items)

    def example_context(self):
        """Example using PromptContext."""
        items = [
            "First item",
            "Second item",
            "Third item"
        ]
        self.class_with_context.list(items=items)

    def simple_list(self) -> Optional[ListPromptResponse]:
        """Show a simple list example."""
        items = [
            "First item",
            "Second item",
            "Third item"
        ]
        return self.io_manager.list(items=items)

    def nested_list(self) -> Optional[ListPromptResponse]:
        """Show a nested list example."""
        items = [
            "Root item 1",
            "  Subitem 1.1",
            "  Subitem 1.2",
            "    Subitem 1.2.1",
            "Root item 2",
            "  Subitem 2.1"
        ]
        return self.io_manager.list(items=items)

    def colored_list(self) -> Optional[ListPromptResponse]:
        """Show a colored list example."""
        items = [
            "Success item",
            "Warning item",
            "Error item"
        ]
        return self.io_manager.list(
            items=items,
            color=TerminalColor.GREEN
        )

    def custom_bullet(self) -> Optional[ListPromptResponse]:
        """Show a list with custom bullet character."""
        items = [
            "First item",
            "Second item",
            "Third item"
        ]
        return self.io_manager.list(
            items=items,
            bullet="-"
        )
