"""Example for properties response."""
from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.data.properties_prompt_response import PropertiesPromptResponse


class PropertiesExample(AbstractResponseExample):
    """Example for properties response."""

    def get_example(self) -> str:
        properties = {
            "name": "John Doe",
            "age": 30,
            "contact": {
                "email": "john@example.com",
                "phone": "123-456-7890"
            }
        }
        response = PropertiesPromptResponse.create_properties(
            properties=properties,
            title="User Information",
            context=self.io_manager.create_context()
        )
        return response.render()

    def example_class(self, indentation: Optional[int] = None):
        """Example using class with context."""
        properties = {
            "name": "John Doe",
            "age": 30,
            "contact": {
                "email": "john@example.com",
                "phone": "123-456-7890"
            }
        }
        context = self.io_manager.create_context()
        if indentation is not None:
            context.indentation = indentation
        return PropertiesPromptResponse.create_properties(
            properties=properties,
            title="User Information",
            context=context
        )

    def example_manager(self):
        """Example using IoManager directly."""
        properties = {
            "server": "localhost",
            "port": 8080,
            "config": {
                "debug": True,
                "log_level": "INFO"
            }
        }
        self.io_manager.properties(
            properties=properties,
            title="Server Configuration"
        )

    def example_context(self):
        """Example using context."""
        properties = {
            "status": "success",
            "duration": "2.5s",
            "details": {
                "processed": 100,
                "failed": 0
            }
        }
        self.class_with_context.properties(
            properties=properties,
            title="Operation Results"
        )
