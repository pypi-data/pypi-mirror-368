"""Step-based progress context implementation."""
from typing import List, Any, Optional, TypeVar, Generic, Callable
from dataclasses import dataclass
import time

from wexample_prompt.common.prompt_context import PromptContext


# Type variable for step function return type
T = TypeVar('T')


@dataclass
class ProgressStep(Generic[T]):
    """Represents a single step in a progress sequence."""
    callback: Callable[..., T]
    description: str
    weight: float = 1.0


class StepProgressContext:
    """Context manager for step-based progress."""
    
    def __init__(
        self,
        steps: List[ProgressStep],
        total_weight: float,
        width: int = 50,
        title: Optional[str] = None,
        context: Optional[PromptContext] = None
    ):
        """Initialize the progress context.
        
        Args:
            steps: List of steps to execute
            total_weight: Total weight of all steps
            width: Progress bar width
            title: Optional title
            context: Optional prompt context for formatting
        """
        self.steps = steps
        self.total_weight = total_weight
        self.width = width
        self.title = title
        self.context = context
        self.current_weight = 0.0
        self.start_time = 0.0
        
    def __enter__(self) -> 'StepProgressContext':
        """Start the progress context."""
        self.start_time = time.time()
        # Show initial progress
        self._update_progress(self.steps[0].description if self.steps else "Starting")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up after progress is complete."""
        pass
        
    def _update_progress(self, description: str) -> None:
        # Avoid circular import
        from wexample_prompt.responses.interactive.progress_prompt_response import ProgressPromptResponse

        """Update the progress display.
        
        Args:
            description: Current step description
        """
        # Calculate percentage
        percentage = int(100 * self.current_weight / self.total_weight)
        
        # Create progress bar with label
        label = f"{self.title}: {description}" if self.title else description
        
        # Use carriage return to overwrite previous line
        progress = ProgressPromptResponse.create_progress(
            total=100,
            current=percentage,
            width=self.width,
            label=label,
            context=self.context
        )
        progress.print(end="\n", flush=True)
        
    def execute_steps(self) -> List[Any]:
        """Execute all steps and return their results.
        
        Returns:
            List of results from each step
        
        Raises:
            Exception: If any step fails
        """
        results = []
        
        for step in self.steps:
            # Execute step
            result = step.callback()
            if result is False:
                raise Exception(f"Step failed: {step.description}")
                
            results.append(result)
            
            # Update progress
            self.current_weight += step.weight
            
            # Show progress for next step or completion
            if step != self.steps[-1]:
                next_step = self.steps[self.steps.index(step) + 1]
                self._update_progress(next_step.description)
            else:
                self._update_progress("Complete")
                
        return results
