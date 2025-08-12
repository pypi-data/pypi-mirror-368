from abc import abstractmethod
from typing import Protocol, TypeVar, TYPE_CHECKING, Dict, Any, Optional, List, Union

if TYPE_CHECKING:
    from wexample_prompt.responses.titles.title_prompt_response import TitlePromptResponse
    from wexample_prompt.responses.titles.subtitle_prompt_response import SubtitlePromptResponse
    from wexample_prompt.responses.messages.log_prompt_response import LogPromptResponse
    from wexample_prompt.responses.messages.info_prompt_response import InfoPromptResponse
    from wexample_prompt.responses.messages.debug_prompt_response import DebugPromptResponse
    from wexample_prompt.responses.messages.error_prompt_response import ErrorPromptResponse
    from wexample_prompt.responses.messages.failure_prompt_response import FailurePromptResponse
    from wexample_prompt.responses.messages.success_prompt_response import SuccessPromptResponse
    from wexample_prompt.responses.messages.task_prompt_response import TaskPromptResponse
    from wexample_prompt.responses.messages.warning_prompt_response import WarningPromptResponse
    from wexample_prompt.responses.data.list_prompt_response import ListPromptResponse
    from wexample_prompt.responses.data.table_prompt_response import TablePromptResponse
    from wexample_prompt.responses.data.tree_prompt_response import TreePromptResponse
    from wexample_prompt.responses.data.properties_prompt_response import PropertiesPromptResponse
    from wexample_prompt.responses.data.suggestions_prompt_response import SuggestionsPromptResponse
    from wexample_prompt.responses.interactive.progress_prompt_response import ProgressPromptResponse
    from wexample_prompt.responses.data.multiple_prompt_response import MultiplePromptResponse
    from wexample_prompt.responses.interactive.choice_prompt_response import ChoicePromptResponse
    from wexample_prompt.responses.interactive.choice_dict_prompt_response import ChoiceDictPromptResponse
    from wexample_prompt.responses.interactive.file_picker_prompt_response import FilePickerPromptResponse
    from wexample_prompt.responses.interactive.dir_picker_prompt_response import DirPickerPromptResponse

T = TypeVar('T', bound='BasePromptResponse')


class IoHandlerProtocol(Protocol):
    # Titles
    @abstractmethod
    def title(self, message: str, **kwargs) -> "TitlePromptResponse":
        pass

    @abstractmethod
    def subtitle(self, message: str, **kwargs) -> "SubtitlePromptResponse":
        pass

    # Messages
    @abstractmethod
    def log(self, message: str, **kwargs) -> "LogPromptResponse":
        pass

    @abstractmethod
    def info(self, message: str, **kwargs) -> "InfoPromptResponse":
        pass

    @abstractmethod
    def debug(self, message: str, **kwargs) -> "DebugPromptResponse":
        pass

    @abstractmethod
    def error(self, message: str, exception: Optional[Exception] = None, fatal: bool = True, **kwargs) -> "ErrorPromptResponse":
        pass

    @abstractmethod
    def failure(self, message: str, **kwargs) -> "FailurePromptResponse":
        pass

    @abstractmethod
    def success(self, message: str, **kwargs) -> "SuccessPromptResponse":
        pass

    @abstractmethod
    def task(self, message: str, **kwargs) -> "TaskPromptResponse":
        pass

    @abstractmethod
    def warning(self, message: str, **kwargs) -> "WarningPromptResponse":
        pass

    # Data display
    @abstractmethod
    def list(self, items: list, **kwargs) -> "ListPromptResponse":
        pass

    @abstractmethod
    def table(self, data: list, **kwargs) -> "TablePromptResponse":
        pass

    @abstractmethod
    def tree(self, data: Dict[str, Any], **kwargs) -> "TreePromptResponse":
        pass

    @abstractmethod
    def properties(self, properties: Dict[str, Any], **kwargs) -> "PropertiesPromptResponse":
        pass

    @abstractmethod
    def suggestions(self, suggestions: List[str], **kwargs) -> "SuggestionsPromptResponse":
        pass

    # Progress
    @abstractmethod
    def progress(self, total: int, message: Optional[str] = None, **kwargs) -> "ProgressPromptResponse":
        pass

    # Multiple responses
    @abstractmethod
    def multiple(self, responses: List[T], **kwargs) -> "MultiplePromptResponse":
        pass

    # Interactive
    @abstractmethod
    def choice(self, choices: List[str], message: Optional[str] = None, **kwargs) -> "ChoicePromptResponse":
        pass

    @abstractmethod
    def choice_dict(self, choices: Dict[str, Any], message: Optional[str] = None, **kwargs) -> "ChoiceDictPromptResponse":
        pass

    @abstractmethod
    def file_picker(self, path: str, pattern: Optional[str] = None, **kwargs) -> "FilePickerPromptResponse":
        pass

    @abstractmethod
    def dir_picker(self, path: str, **kwargs) -> "DirPickerPromptResponse":
        pass
