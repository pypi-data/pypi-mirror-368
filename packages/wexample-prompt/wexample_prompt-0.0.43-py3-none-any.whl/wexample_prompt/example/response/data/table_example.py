"""Example for table response."""
from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.data.table_prompt_response import TablePromptResponse


class TableExample(AbstractResponseExample):
    """Example for table response."""

    def get_example(self) -> str:
        headers = ["Name", "Age", "City"]
        data = [
            ["John", "30", "New York"],
            ["Jane", "25", "San Francisco"],
            ["Bob", "35", "Chicago"]
        ]
        response = TablePromptResponse.create_table(
            data=data,
            headers=headers,
            title="Employee List",
            context=self.io_manager.create_context()
        )
        return response.render()

    def example_class(self, indentation: Optional[int] = None):
        """Example using class with context."""
        headers = ["Name", "Age", "City"]
        data = [
            ["John", "30", "New York"],
            ["Jane", "25", "San Francisco"],
            ["Bob", "35", "Chicago"]
        ]
        context = self.io_manager.create_context()
        if indentation is not None:
            context.indentation = indentation
        return TablePromptResponse.create_table(
            data=data,
            headers=headers,
            title="Employee List",
            context=context
        )

    def example_manager(self):
        """Example using IoManager directly."""
        headers = ["Name", "Age", "City"]
        data = [
            ["John", "30", "New York"],
            ["Jane", "25", "San Francisco"],
            ["Bob", "35", "Chicago"]
        ]
        self.io_manager.table(
            data=data,
            headers=headers,
            title="Employee List"
        )

    def example_context(self):
        """Example using context."""
        headers = ["Name", "Age", "City"]
        data = [
            ["John", "30", "New York"],
            ["Jane", "25", "San Francisco"],
            ["Bob", "35", "Chicago"]
        ]
        self.class_with_context.table(
            data=data,
            headers=headers,
            title="Employee List"
        )
