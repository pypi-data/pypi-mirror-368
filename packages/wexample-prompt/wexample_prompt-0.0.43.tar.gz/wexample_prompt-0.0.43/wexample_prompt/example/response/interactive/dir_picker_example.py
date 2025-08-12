"""Example usage of DirPickerPromptResponse."""

from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.interactive.dir_picker_prompt_response import DirPickerPromptResponse


class DirPickerExample(AbstractResponseExample):

    def example_class(self, indentation: Optional[int] = None):
        return DirPickerPromptResponse.create_dir_picker(
            question="Select a directory:",
            base_dir=None,  # Will use current working directory
            context=self.io_manager.create_context(indentation=indentation)
        )

    def example_manager(self):
        self.io_manager.dir_picker("Select a directory:")

    def example_context(self):
        self.class_with_context.dir_picker("Select a directory:")
