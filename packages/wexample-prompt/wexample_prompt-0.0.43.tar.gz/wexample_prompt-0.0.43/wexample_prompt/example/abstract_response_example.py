from abc import abstractmethod
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel

from wexample_prompt.mixins.with_io_manager import WithIoManager

if TYPE_CHECKING:
    from wexample_prompt.example.example_class_with_context import ExampleClassWithContext


class AbstractResponseExample(WithIoManager, BaseModel):
    class_with_context: Optional["ExampleClassWithContext"] = None

    def __init__(self, **kwargs):
        from wexample_prompt.common.io_manager import IoManager
        from wexample_prompt.example.example_class_with_context import ExampleClassWithContext

        super().__init__(**kwargs)

        self.io_manager = IoManager()
        self.class_with_context = ExampleClassWithContext(io_manager=self.io_manager)

    @abstractmethod
    def example_class(self, indentation: Optional[int] = None):
        pass

    @abstractmethod
    def example_manager(self):
        pass

    @abstractmethod
    def example_context(self):
        pass
