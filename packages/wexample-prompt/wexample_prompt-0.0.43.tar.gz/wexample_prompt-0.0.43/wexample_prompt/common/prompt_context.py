import shutil
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

from wexample_prompt.enums.verbosity_level import VerbosityLevel


class PromptContext(BaseModel):
    """Context for rendering responses, including terminal information."""
    terminal_width: int = Field(
        default_factory=lambda: shutil.get_terminal_size().columns
    )
    is_tty: bool = Field(
        default_factory=lambda: hasattr(shutil.sys.stdout, 'isatty')
                                and shutil.sys.stdout.isatty()
    )
    color_enabled: bool = Field(default=True)
    indentation: int = Field(default=0)  # Number of indentation levels
    verbosity: VerbosityLevel = Field(default=VerbosityLevel.DEFAULT)
    fatal: bool = Field(default=False, description="If True, process will exit after printing")
    exit_code: int = Field(default=1, description="Exit code to use when fatal is True")
    params: Optional[Dict[str, Any]] = None

    def get_effective_width(self) -> int:
        """Get the effective width considering terminal constraints."""
        return (min(self.terminal_width, 120)  # Cap at reasonable width
                - self.indentation)

    def should_use_color(self) -> bool:
        """Determine if color should be used."""
        return self.color_enabled and self.is_tty

    def get_indentation_spaces_count(self) -> int:
        from wexample_prompt.const.formatting import INDENTATION_SPACES
        return self.indentation * INDENTATION_SPACES

    def get_indentation(self) -> str:
        """Get the current indentation string."""
        return " " * self.get_indentation_spaces_count()

    def should_show_message(self, required_verbosity: Optional[VerbosityLevel]) -> bool:
        """Check if a message should be shown based on verbosity level.
        
        Args:
            required_verbosity: The minimum verbosity level required to show the message.
                              If None, the message will always be shown.
            
        Returns:
            bool: True if the message should be shown, False otherwise
            
        Example:
            - None -> True (always show)
            - QUIET message (0) in QUIET context (0) -> True
            - MAXIMUM message (3) in QUIET context (0) -> False
            - QUIET message (0) in MAXIMUM context (3) -> True
            - MAXIMUM message (3) in MAXIMUM context (3) -> True
        """
        if required_verbosity is None:
            return True
        return required_verbosity <= self.verbosity

    def format_message(self, message: str) -> str:
        if self.params:
            return message.format(**self.params)
        return message
