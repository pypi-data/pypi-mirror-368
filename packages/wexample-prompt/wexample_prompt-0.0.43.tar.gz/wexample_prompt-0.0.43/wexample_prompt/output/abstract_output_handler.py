from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse


class AbsractOutputHandler(BaseModel):
    def print(self, response: "AbstractPromptResponse") -> None:
        ...
