from typing import Optional

from InquirerPy.base.control import Choice

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.interactive.choice_prompt_response import ChoicePromptResponse


class ChoiceExample(AbstractResponseExample):

    def example_class(self, indentation: Optional[int] = None):
        choices = [
            Choice(value="value1", name="Choice 1"),
            Choice(value="value2", name="Choice 2"),
            Choice(value="value3", name="Choice 3")
        ]
        return ChoicePromptResponse.create_choice(
            question="Select an option:",
            choices=choices,
            context=self.io_manager.create_context(indentation=indentation)
        )

    def example_manager(self):
        choices = ["Option 1", "Option 2", "Option 3"]
        self.io_manager.choice("Select an option:", choices)

    def example_context(self):
        choices = ["Option 1", "Option 2", "Option 3"]
        self.class_with_context.choice("Select an option:", choices)
