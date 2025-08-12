"""Core color management utilities for terminal output."""
import os
import sys
from typing import Dict, Optional

from colorama import init, Style
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.enums.terminal_color import TerminalColor


class ColorManager:
    """Manages color application and terminal capabilities."""
    
    # Initialize colorama when class is loaded
    init()
    
    # Default message type to color mapping
    MESSAGE_COLORS: Dict[MessageType, TerminalColor] = {
        MessageType.ALERT: TerminalColor.LIGHT_YELLOW,
        MessageType.CRITICAL: TerminalColor.LIGHT_RED,
        MessageType.DEBUG: TerminalColor.CYAN,
        MessageType.ERROR: TerminalColor.RED,
        MessageType.FAILURE: TerminalColor.RED,
        MessageType.INFO: TerminalColor.LIGHT_BLUE,
        MessageType.LOG: TerminalColor.WHITE,
        MessageType.SUCCESS: TerminalColor.GREEN,
        MessageType.TASK: TerminalColor.MAGENTA,
        MessageType.WARNING: TerminalColor.YELLOW,
    }
    
    @classmethod
    def supports_color(cls) -> bool:
        """Check if the current terminal supports color output."""
        # Check if NO_COLOR environment variable is set
        if os.environ.get('NO_COLOR') is not None:
            return False
            
        # Check if we're in a TTY
        if not sys.stdout.isatty():
            return False
            
        # With colorama, Windows support is handled automatically
        return True
    
    @classmethod
    def colorize(cls, text: str, color: Optional[TerminalColor] = None, 
                style: Optional[TerminalColor] = None) -> str:
        """Add color and style to text if supported.
        
        Args:
            text (str): The text to colorize
            color (Optional[TerminalColor]): The color to use
            style (Optional[TerminalColor]): The style to use
            
        Returns:
            str: The colorized text if supported, original text otherwise
        """
        if not cls.supports_color():
            return text
            
        prefix = ''
        if color:
            prefix += str(color)
        if style:
            prefix += str(style)
            
        if prefix:
            return f"{prefix}{text}{Style.RESET_ALL}"
        return text
    
    @classmethod
    def get_message_color(cls, message_type: MessageType) -> TerminalColor:
        """Get the color for a specific message type.
        
        Args:
            message_type (MessageType): The message type
            
        Returns:
            TerminalColor: The color for the message type
        """
        return cls.MESSAGE_COLORS.get(message_type, TerminalColor.DEFAULT)
