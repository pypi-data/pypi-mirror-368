from typing import Optional, Any

from wexample_prompt.mixins.with_io_manager import WithIoManager


class WithPromptContext(
    WithIoManager
):
    prompt_context_parent: Optional[Any] = None
    _context_indent: int = 2  # Number of spaces for each indentation level

    def __getattr__(self, name: str):
        if hasattr(self.io, name):
            attr = getattr(self.io, name)

            if callable(attr):
                def wrapper(*args, **kwargs):
                    if args:
                        formatted_msg = self.format_message(args[0])
                        args = (formatted_msg,) + args[1:]
                    return attr(*args, **kwargs)

                return wrapper

            return attr

        return super().__getattr__(name)

    def get_prompt_context_parent(self) -> Optional['WithPromptContext']:
        """Get the parent context for indentation. By default, returns None."""
        return self.prompt_context_parent

    def set_prompt_context_parent(self, parent: 'WithPromptContext') -> None:
        """Set the parent context for indentation."""
        self.prompt_context_parent = parent

    def get_context_indent_level(self) -> int:
        """Calculate the indentation level based on parent contexts."""
        parent = self.get_prompt_context_parent()
        if parent is None:
            return 0
        return parent.get_context_indent_level() + 1

    def format_message(self, message: str) -> str:
        """Format the message according to the bullet point style."""
        indent = " " * (self.get_context_indent_level() * self._context_indent)
        context_name = self.__class__.__name__

        if self.io._last_context != context_name:
            self.io._last_context = context_name
            return self._format_context_prompt_message(
                message=message,
                indent=indent
            )

        return f"{indent}  ⋮ {message}"

    def _format_context_prompt_message(self, message: str, indent: str) -> str:
        return f"{indent}[{self.__class__.__name__}]: {message}"

    def _format_if_message(self, message: Optional[str]) -> Optional[str]:
        """Format message if it exists, otherwise return None."""
        return self.format_message(message) if message else None
