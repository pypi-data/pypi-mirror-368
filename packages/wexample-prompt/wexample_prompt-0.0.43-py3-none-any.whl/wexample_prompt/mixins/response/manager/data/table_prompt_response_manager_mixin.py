"""Mixin for handling table responses in IoManager."""
from typing import List, Optional, Any, TYPE_CHECKING

from wexample_prompt.enums.verbosity_level import VerbosityLevel

if TYPE_CHECKING:
    from wexample_prompt.responses.data.table_prompt_response import TablePromptResponse


class TablePromptResponseManagerMixin:
    """Mixin for IoManager to handle table responses."""

    def table(
        self,
        data: List[List[Any]],
        headers: Optional[List[str]] = None,
        title: Optional[str] = None,
        **kwargs
    ) -> "TablePromptResponse":
        """Create and display a table response.

        Args:
            data: List of rows, each row being a list of values
            headers: Optional list of column headers
            title: Optional table title
            **kwargs: Additional arguments passed to create_table
        """
        from wexample_prompt.responses.data.table_prompt_response import TablePromptResponse

        response = TablePromptResponse.create_table(
            data=data,
            headers=headers,
            title=title,
            context=self.create_context(),
            **kwargs
        )

        self.print_response(response)
        return response
