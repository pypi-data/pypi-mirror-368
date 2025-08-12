"""Progress bar response implementation."""
from typing import List, Callable, Optional, Any, ClassVar, Dict, Type

from wexample_prompt.responses.base_prompt_response import BasePromptResponse
from wexample_prompt.enums.response_type import ResponseType
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.common.color_manager import ColorManager
from wexample_prompt.progress.step_progress_context import (
    ProgressStep,
    StepProgressContext
)


class ProgressPromptResponse(BasePromptResponse):
    """Response for displaying progress bars."""
    
    # Class variables properly annotated for pydantic
    FILL_CHAR: ClassVar[str] = "▰"  # Filled block
    EMPTY_CHAR: ClassVar[str] = "▱"  # Empty block
    
    # ANSI color codes
    CYAN: ClassVar[str] = "\033[36m"
    BLUE: ClassVar[str] = "\033[34m"
    GREEN: ClassVar[str] = "\033[32m"
    RESET: ClassVar[str] = "\033[0m"

    # Instance variables
    total: int
    current: int
    width: int = 50
    label: Optional[str] = None
    color: Optional[TerminalColor] = None

    @classmethod
    def get_example_class(cls) -> Type:
        """Get the example class for this response type.

        Returns:
            Type: The example class
        """
        from wexample_prompt.example.response.interactive.progress_example import ProgressExample
        return ProgressExample

    @classmethod
    def set_style(cls, fill_char: str = "▰", empty_char: str = "▱"):
        """Set the progress bar style characters.
        
        Args:
            fill_char: Character to use for filled portion
            empty_char: Character to use for empty portion
        """
        cls.FILL_CHAR = fill_char
        cls.EMPTY_CHAR = empty_char
    
    @classmethod
    def create_progress(
        cls,
        total: int,
        current: int,
        width: int = 50,
        label: Optional[str] = None,
        context: Optional[PromptContext] = None,
        color: Optional[TerminalColor] = None,
        **kwargs: Any
    ) -> 'ProgressPromptResponse':
        """Create a simple progress bar response.
        
        Args:
            total: Total number of items
            current: Current progress
            width: Width of the progress bar in characters
            label: Optional label to show above the progress bar
            context: Optional prompt context for formatting
            color: Optional color for the progress bar
            **kwargs: Additional arguments
            
        Raises:
            ValueError: If total or current are negative, or if width is less than 1
            ZeroDivisionError: If total is zero
        """
        if total <= 0:
            raise ValueError("Total must be greater than 0")
        if current < 0:
            raise ValueError("Current progress cannot be negative")
        if width < 1:
            raise ValueError("Width must be at least 1")
            
        # If label is provided and color is specified, colorize it
        if label and color:
            label = ColorManager.colorize(label, color)

        return cls(
            lines=[],  # Lines will be generated in render()
            response_type=ResponseType.PROGRESS,
            total=total,
            current=current,
            width=width,
            label=label,
            color=color,
            context=context
        )

    def render(self) -> str:
        """Render the progress bar with current state."""
        # Cap current at total
        current = min(self.current, self.total)
        
        percentage = min(100, int(100 * current / self.total))
        filled = int(self.width * current / self.total)
        
        # Choose color based on progress or use specified color
        if self.color:
            color = str(self.color)
            reset = self.RESET
        else:
            # No color codes if color is explicitly set to None
            color = ""
            reset = ""
            
        # Build progress bar without brackets
        bar = (
            color +
            self.FILL_CHAR * filled +
            self.EMPTY_CHAR * (self.width - filled) +
            reset
        )
        
        # If we have a label, include the progress bar on the same line
        if self.label:
            text = f"{self.label} {bar} {percentage}%"
            segments = [PromptResponseSegment(text=text)]
        else:
            text = f"{bar} {percentage}%"
            segments = [PromptResponseSegment(text=text)]
            
        # Update lines and render
        self.lines = [PromptResponseLine(segments=segments)]
        return super().render()
    
    @classmethod
    def create_steps(
        cls,
        steps: List[ProgressStep],
        width: int = 50,
        title: Optional[str] = None,
        context: Optional[PromptContext] = None
    ) -> StepProgressContext:
        """Create a step-based progress context.
        
        Args:
            steps: List of progress steps to execute
            width: Width of the progress bar
            title: Optional title for the progress bar
            context: Optional prompt context for formatting
            
        Returns:
            StepProgressContext to be used in a with statement
        """
        total_weight = sum(step.weight for step in steps)
        return StepProgressContext(
            steps=steps,
            total_weight=total_weight,
            width=width,
            title=title,
            context=context
        )
    
    @classmethod
    def execute(
        cls,
        callbacks: List[Callable[..., Any]],
        width: int = 50,
        title: Optional[str] = None,
        context: Optional[PromptContext] = None
    ) -> List[Any]:
        """Execute a list of callbacks with progress tracking.
        
        This is a simplified version that takes just a list of callback functions.
        It automatically extracts descriptions from docstrings or function names.
        
        Args:
            callbacks: List of callback functions to execute
            width: Width of the progress bar
            title: Optional title for the progress bar
            context: Optional prompt context for formatting
            
        Returns:
            List of results from each callback
            
        Example:
            ```python
            ProgressPromptResponse.execute([
                step1,
                step2,
                step3
            ])
            ```
        """
        # Create progress steps from callbacks
        steps = []
        for callback in callbacks:
            import inspect

            # Try to get description from docstring
            doc = inspect.getdoc(callback)
            description = doc.split("\n")[0] if doc else callback.__name__
            
            steps.append(ProgressStep(
                callback=callback,
                description=description,
                weight=1
            ))
            
        # Create context and execute steps
        with cls.create_steps(steps, width, title, context) as progress:
            return progress.execute_steps()
