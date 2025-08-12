"""Abstract base class for interactive prompt responses."""
from abc import ABC

from wexample_prompt.responses.base_prompt_response import BasePromptResponse


class AbstractInteractivePromptResponse(BasePromptResponse, ABC):
    pass
