from abc import ABC, abstractmethod

from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.enums.terminal_color import TerminalColor


class AbstractPromptTheme(ABC):
    """Abstract base class for prompt themes."""
    
    @abstractmethod
    def get_color(self, message_type: MessageType) -> TerminalColor:
        """Get color for message type."""
        pass
