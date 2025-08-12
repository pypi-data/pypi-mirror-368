from pydantic import BaseModel

from wexample_prompt.mixins.with_prompt_context import WithPromptContext


class ExampleClassWithContext(WithPromptContext, BaseModel):
    def _format_context_prompt_message(self, message: str, indent: str) -> str:
        return f"{indent}[EXAMPLE|{self.__class__.__name__}]: {message}"
