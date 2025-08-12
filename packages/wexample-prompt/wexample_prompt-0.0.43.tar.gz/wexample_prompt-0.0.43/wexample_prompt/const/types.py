from typing import TypedDict, Optional


class LineDict(TypedDict, total=False):
    message: str
    type: Optional[str]
