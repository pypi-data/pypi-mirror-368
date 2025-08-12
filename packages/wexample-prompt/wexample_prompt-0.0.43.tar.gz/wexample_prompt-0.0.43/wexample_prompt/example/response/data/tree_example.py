"""Example for tree response."""
from typing import Optional

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.data.tree_prompt_response import TreePromptResponse


class TreeExample(AbstractResponseExample):
    """Example for tree response."""

    def get_example(self) -> str:
        data = {
            "root": {
                "folder1": {
                    "file1": "content1",
                    "file2": "content2"
                },
                "folder2": {
                    "subfolder": {
                        "file3": "content3"
                    }
                }
            }
        }
        response = TreePromptResponse.create_tree(
            data=data,
            context=self.io_manager.create_context()
        )
        return response.render()

    def example_class(self, indentation: Optional[int] = None):
        """Example using class with context."""
        data = {
            "root": {
                "folder1": {
                    "file1": "content1",
                    "file2": "content2"
                },
                "folder2": {
                    "subfolder": {
                        "file3": "content3"
                    }
                }
            }
        }
        context = self.io_manager.create_context()
        if indentation is not None:
            context.indentation = indentation
        return TreePromptResponse.create_tree(
            data=data,
            context=context
        )

    def example_manager(self):
        """Example using IoManager directly."""
        data = {
            "root": {
                "folder1": {
                    "file1": "content1",
                    "file2": "content2"
                },
                "folder2": {
                    "subfolder": {
                        "file3": "content3"
                    }
                }
            }
        }
        self.io_manager.tree(data=data)

    def example_context(self):
        """Example using context."""
        data = {
            "root": {
                "folder1": {
                    "file1": "content1",
                    "file2": "content2"
                },
                "folder2": {
                    "subfolder": {
                        "file3": "content3"
                    }
                }
            }
        }
        self.class_with_context.tree(data=data)
