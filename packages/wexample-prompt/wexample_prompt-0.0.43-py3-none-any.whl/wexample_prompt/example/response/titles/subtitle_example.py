from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.titles.subtitle_prompt_response import SubtitlePromptResponse


class SubtitleExample(AbstractResponseExample):

    def example_class(self, indentation: Optional[int] = None):
        return SubtitlePromptResponse.create_subtitle(
            'Test subtitle',
            context=self.io_manager.create_context(indentation=indentation),
            indentation=indentation
        )

    def example_manager(self):
        self.io_manager.subtitle('Test subtitle')

    def example_context(self):
        self.class_with_context.subtitle('Test subtitle')
