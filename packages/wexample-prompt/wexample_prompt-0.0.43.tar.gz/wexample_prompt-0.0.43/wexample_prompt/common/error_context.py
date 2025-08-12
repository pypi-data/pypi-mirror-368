from wexample_prompt.common.prompt_context import PromptContext
from pydantic import Field
from typing import Optional, Dict, Any
import traceback


class ErrorContext(PromptContext):
    """Context for error messages."""

    is_fatal: bool = Field(
        default=False,
        description="Whether this is a fatal error that should exit the program"
    )
    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Parameters to format the message with"
    )
    indentation: int = Field(
        default=0,
        description="Indentation level for the message"
    )
