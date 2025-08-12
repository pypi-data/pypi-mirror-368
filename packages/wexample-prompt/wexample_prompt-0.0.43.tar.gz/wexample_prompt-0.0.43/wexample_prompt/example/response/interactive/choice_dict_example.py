from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.interactive.choice_dict_prompt_response import ChoiceDictPromptResponse


class ChoiceDictExample(AbstractResponseExample):

    def example_class(self, indentation: Optional[int] = None):
        choices = {
            "key1": "Choice 1",
            "key2": "Choice 2",
            "key3": "Choice 3"
        }
        return ChoiceDictPromptResponse.create_choice_dict(
            question="Select an option:",
            choices=choices,
            context=self.io_manager.create_context(indentation=indentation)
        )

    def example_manager(self):
        choices = {
            "key1": "Option 1",
            "key2": "Option 2",
            "key3": "Option 3"
        }
        self.io_manager.choice_dict("Select an option:", choices)

    def example_context(self):
        choices = {
            "key1": "Option 1",
            "key2": "Option 2",
            "key3": "Option 3"
        }
        self.class_with_context.choice_dict("Select an option:", choices)
