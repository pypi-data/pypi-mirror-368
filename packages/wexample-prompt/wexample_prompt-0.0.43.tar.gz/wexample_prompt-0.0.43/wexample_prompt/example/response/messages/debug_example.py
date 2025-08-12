from typing import TYPE_CHECKING, Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.debug_prompt_response import DebugPromptResponse

if TYPE_CHECKING:
    from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse

class DebugExample(AbstractResponseExample):

    def example_class(self, indentation: Optional[int] = None) -> "AbstractPromptResponse":
        """Example using the class directly."""
        return DebugPromptResponse.create_debug(
            'Test debug message',
            context=self.io_manager.create_context(indentation=indentation)
        )

    def example_manager(self):
        self.io_manager.debug('Test debug message')

    def example_context(self):
        self.class_with_context.debug('Test debug message')
