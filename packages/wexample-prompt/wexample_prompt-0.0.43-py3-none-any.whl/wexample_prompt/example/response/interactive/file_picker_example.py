"""Example usage of FilePickerPromptResponse."""

from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.interactive.file_picker_prompt_response import FilePickerPromptResponse


class FilePickerExample(AbstractResponseExample):
    """Example usage of FilePickerPromptResponse."""

    def example_class(self, indentation: Optional[int] = None):
        """Example using the class directly."""
        return FilePickerPromptResponse.create_file_picker(
            question="Select a file:",
            base_dir=None,  # Will use current working directory
            context=self.io_manager.create_context(indentation=indentation)
        )

    def example_manager(self):
        """Example using the IoManager."""
        self.io_manager.file_picker("Select a file:")

    def example_context(self):
        """Example using PromptContext."""
        self.class_with_context.file_picker("Select a file:")
