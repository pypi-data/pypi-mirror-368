"""Response for displaying and handling directory picker prompts."""
import os
from typing import Any, Dict, Optional, Type

from wexample_prompt.responses.interactive.choice_dict_prompt_response import ChoiceDictPromptResponse
from wexample_helpers.helpers.dict import dict_sort_values


class DirPickerPromptResponse(ChoiceDictPromptResponse):
    """Response for displaying a directory picker interface."""

    @classmethod
    def get_example_class(cls) -> Type:
        """Get the example class for this response type.

        Returns:
            Type: The example class
        """
        from wexample_prompt.example.response.interactive.dir_picker_example import DirPickerExample
        return DirPickerExample

    @classmethod
    def create_dir_picker(
        cls,
        base_dir: Optional[str] = None,
        question: str = "Select a directory:",
        abort: Optional[str] = "> Abort",
        **kwargs: Any
    ) -> 'DirPickerPromptResponse':
        """Create a directory picker prompt response.
        
        Args:
            base_dir: Starting directory (defaults to current working directory)
            question: The question to display
            abort: Optional abort choice text
            **kwargs: Additional arguments for inquirer.select
            
        Returns:
            DirPickerPromptResponse: A new directory picker prompt response
        """
        base_dir = base_dir or os.getcwd()
        
        # Initialize choices with parent directory
        choices_dirs: Dict[str, str] = {"..": ".."}
        
        # List directories only
        for element in os.listdir(base_dir):
            full_path = os.path.join(base_dir, element)
            if os.path.isdir(full_path):
                element_label = f" {element}"
                choices_dirs[element] = element_label
                
        # Sort directories
        choices_dirs = dict_sort_values(choices_dirs)
        
        # Add option to select current directory
        choices_dirs[base_dir] = "> Select this directory"
        
        # Get color from kwargs
        color = kwargs.pop('color', None)
        
        # Create response
        response = super().create_choice_dict(
            question=question,
            choices=choices_dirs,
            abort=abort,
            color=color,
            **kwargs
        )
        
        # Store base directory for execute()
        response._base_dir = base_dir
        return response
        
    def execute(self) -> Optional[str]:
        """Execute the directory picker prompt and get selected path.
        
        Returns:
            str: Full path to selected directory, or None if aborted
        """
        selected = super().execute()
        if not selected:
            return None
            
        # If current directory selected, return it
        if selected == self._base_dir:
            return selected
            
        # Otherwise, join with base dir and recurse if needed
        full_path = os.path.join(self._base_dir, selected)
        if os.path.isdir(full_path):
            next_response = self.__class__.create_dir_picker(
                base_dir=full_path,
                question=self.lines[0].render()  # Keep same question
            )
            return next_response.execute()
            
        return None
