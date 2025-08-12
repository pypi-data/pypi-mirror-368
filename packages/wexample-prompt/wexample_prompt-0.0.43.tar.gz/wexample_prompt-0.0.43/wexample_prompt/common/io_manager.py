import logging
import shutil
import sys
from logging import Logger
from typing import Any, List, Optional, TextIO, Type, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.mixins.response.manager.base_prompt_response_manager_mixin import \
    BasePromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.data.list_prompt_response_manager_mixin import \
    ListPromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.data.multiple_prompt_response_manager_mixin import \
    MultiplePromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.data.properties_prompt_response_manager_mixin import \
    PropertiesPromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.data.suggestions_prompt_response_manager_mixin import \
    SuggestionsPromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.data.table_prompt_response_manager_mixin import \
    TablePromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.data.tree_prompt_response_manager_mixin import \
    TreePromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.interactive.choice_dict_prompt_response_manager_mixin import \
    ChoiceDictPromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.interactive.choice_prompt_response_manager_mixin import \
    ChoicePromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.interactive.dir_picker_prompt_response_manager_mixin import \
    DirPickerPromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.interactive.file_picker_prompt_response_manager_mixin import \
    FilePickerPromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.interactive.progress_prompt_response_manager_mixin import \
    ProgressPromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.messages.debug_prompt_response_manager_mixin import \
    DebugPromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.messages.error_prompt_response_manager_mixin import \
    ErrorPromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.messages.failure_prompt_response_manager_mixin import \
    FailurePromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.messages.info_prompt_response_manager_mixin import \
    InfoPromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.messages.log_prompt_response_manager_mixin import \
    LogPromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.messages.success_prompt_response_manager_mixin import \
    SuccessPromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.messages.task_prompt_response_manager_mixin import \
    TaskPromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.messages.warning_prompt_response_manager_mixin import \
    WarningPromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.titles.subtitle_prompt_response_manager_mixin import \
    SubtitlePromptResponseManagerMixin
from wexample_prompt.mixins.response.manager.titles.title_prompt_response_manager_mixin import \
    TitlePromptResponseManagerMixin
from wexample_prompt.mixins.with_indent import WithIndent
from wexample_prompt.output.abstract_output_handler import AbsractOutputHandler
from wexample_prompt.output.strout_output_handler import StdoutOutputHandler
from wexample_prompt.responses import BasePromptResponse
from wexample_prompt.themes.default.abstract_prompt_theme import AbstractPromptTheme
from wexample_prompt.themes.default.default_prompt_theme import DefaultPromptTheme

if TYPE_CHECKING:
    from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse


class IoManager(
    BaseModel,
    WithIndent,
    BasePromptResponseManagerMixin,
    ChoiceDictPromptResponseManagerMixin,
    # Data
    ListPromptResponseManagerMixin,
    MultiplePromptResponseManagerMixin,
    PropertiesPromptResponseManagerMixin,
    SuggestionsPromptResponseManagerMixin,
    TablePromptResponseManagerMixin,
    TreePromptResponseManagerMixin,
    # Interactive
    ChoicePromptResponseManagerMixin,
    DirPickerPromptResponseManagerMixin,
    FilePickerPromptResponseManagerMixin,
    ProgressPromptResponseManagerMixin,
    # Messages
    DebugPromptResponseManagerMixin,
    InfoPromptResponseManagerMixin,
    LogPromptResponseManagerMixin,
    SuccessPromptResponseManagerMixin,
    TaskPromptResponseManagerMixin,
    WarningPromptResponseManagerMixin,
    FailurePromptResponseManagerMixin,
    ErrorPromptResponseManagerMixin,
    # Titles
    TitlePromptResponseManagerMixin,
    SubtitlePromptResponseManagerMixin,

):
    """Manager for handling I/O operations in the prompt system."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    theme: AbstractPromptTheme = Field(
        default_factory=DefaultPromptTheme,
        description="Theme for customizing colors and styles"
    )
    log_level: int = Field(
        default=logging.INFO,
        description="Minimum log level for file logging"
    )
    log_file: Optional[str] = Field(
        default=None,
        description="Path to log file. If None, file logging is disabled"
    )
    terminal_width: int = Field(
        default_factory=lambda: shutil.get_terminal_size().columns,
        description="Width of the terminal"
    )
    _logger: Optional[Logger] = PrivateAttr(default=None)
    _log_file_handler: Optional[TextIO] = PrivateAttr(default=None)
    _instance_count: int = PrivateAttr(default=0)
    _last_context: Optional[str] = PrivateAttr(default=None)
    output: Optional[AbsractOutputHandler] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._stdout = sys.stdout
        self._last_context = None
        self._init_output()
        self._init_logger()

    @property
    def _tty_width(self) -> int:
        """Alias for terminal_width to maintain backward compatibility."""
        return self.terminal_width

    @_tty_width.setter
    def _tty_width(self, value: int) -> None:
        """Update terminal width when _tty_width is set."""
        self.terminal_width = value

    def _init_output(self):
        self.output = self.output if (self.output is not None) else StdoutOutputHandler()

    def _init_logger(self):
        """Set up logging configuration."""
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(self.log_level)

        # Clear any existing handlers
        self._logger.handlers.clear()

        if self.log_file:
            self._log_file_handler = logging.FileHandler(self.log_file)
            self._logger.addHandler(self._log_file_handler)

    def __del__(self):
        """Clean up resources."""
        if self._log_file_handler:
            self._log_file_handler.close()

    @classmethod
    def get_response_types(cls) -> List[Type["AbstractPromptResponse"]]:
        from wexample_prompt.responses.base_prompt_response import BasePromptResponse
        from wexample_prompt.responses.titles.title_prompt_response import TitlePromptResponse
        from wexample_prompt.responses.titles.subtitle_prompt_response import SubtitlePromptResponse
        from wexample_prompt.responses.messages.log_prompt_response import LogPromptResponse
        from wexample_prompt.responses.messages.info_prompt_response import InfoPromptResponse
        from wexample_prompt.responses.messages.debug_prompt_response import DebugPromptResponse
        from wexample_prompt.responses.messages.success_prompt_response import SuccessPromptResponse
        from wexample_prompt.responses.messages.task_prompt_response import TaskPromptResponse
        from wexample_prompt.responses.messages.warning_prompt_response import WarningPromptResponse
        from wexample_prompt.responses.messages.failure_prompt_response import FailurePromptResponse
        from wexample_prompt.responses.messages.error_prompt_response import ErrorPromptResponse
        from wexample_prompt.responses.interactive.choice_prompt_response import ChoicePromptResponse
        from wexample_prompt.responses.interactive.choice_dict_prompt_response import ChoiceDictPromptResponse
        from wexample_prompt.responses.interactive.dir_picker_prompt_response import DirPickerPromptResponse
        from wexample_prompt.responses.interactive.file_picker_prompt_response import FilePickerPromptResponse
        from wexample_prompt.responses.interactive.progress_prompt_response import ProgressPromptResponse
        from wexample_prompt.responses.data.list_prompt_response import ListPromptResponse
        from wexample_prompt.responses.data.multiple_prompt_response import MultiplePromptResponse
        from wexample_prompt.responses.data.properties_prompt_response import PropertiesPromptResponse
        from wexample_prompt.responses.data.suggestions_prompt_response import SuggestionsPromptResponse
        from wexample_prompt.responses.data.table_prompt_response import TablePromptResponse
        from wexample_prompt.responses.data.tree_prompt_response import TreePromptResponse

        return [
            BasePromptResponse,
            # Data
            ListPromptResponse,
            MultiplePromptResponse,
            PropertiesPromptResponse,
            SuggestionsPromptResponse,
            TablePromptResponse,
            TreePromptResponse,
            # Interactive
            ChoicePromptResponse,
            ChoiceDictPromptResponse,
            DirPickerPromptResponse,
            FilePickerPromptResponse,
            ProgressPromptResponse,
            # Messages
            LogPromptResponse,
            InfoPromptResponse,
            DebugPromptResponse,
            SuccessPromptResponse,
            TaskPromptResponse,
            WarningPromptResponse,
            FailurePromptResponse,
            ErrorPromptResponse,
            # Titles
            TitlePromptResponse,
            SubtitlePromptResponse,
        ]

    def create_context(self, indentation: Optional[int] = 0) -> PromptContext:
        """Create a context with current indentation and terminal width."""
        return PromptContext(
            indentation=indentation or self.log_indent,
            terminal_width=self.terminal_width,
        )

    def print_responses(self, responses: List[BasePromptResponse]) -> None:
        for response in responses:
            self.print_response(response)

    def print_response(self, response: BasePromptResponse) -> None:
        """Print a response using its own context."""
        # If response has a context but no indentation, set it
        if response.context.indentation == 0 and self.log_indent > 0:
            response.context.indentation = self.log_indent

        self.output.print(response)

        # Exit if fatal
        if response.context and response.context.fatal:
            sys.exit(1)

    def get_input(self, prompt: str = "") -> str:
        return input(prompt)

    def print(self, message: Any, **kwargs: Any) -> None:
        # Convert message to response if it's not already one
        if isinstance(message, BasePromptResponse):
            response = message
        else:
            from wexample_prompt.responses.messages.info_prompt_response import InfoPromptResponse
            response = InfoPromptResponse.create_info(str(message))

        self.print_response(response)

    def update_terminal_width(self) -> None:
        """Update terminal width from system."""
        self.terminal_width = shutil.get_terminal_size().columns
