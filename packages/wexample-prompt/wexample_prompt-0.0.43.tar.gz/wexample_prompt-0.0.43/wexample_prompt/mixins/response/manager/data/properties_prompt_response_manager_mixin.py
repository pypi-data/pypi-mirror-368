"""Properties response manager mixin."""
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_prompt.responses.data.properties_prompt_response import PropertiesPromptResponse


class PropertiesPromptResponseManagerMixin:
    """Mixin for IoManager to handle properties responses."""

    def properties(
        self,
        properties: Dict[str, Any],
        title: Optional[str] = None,
        nested_indent: int = 2,
        **kwargs
    ) -> "PropertiesPromptResponse":
        """Create and display a properties response.

        Args:
            properties: Dictionary of properties to display
            title: Optional title for the properties box
            nested_indent: Indentation for nested properties
            **kwargs: Additional arguments passed to create_properties
        """
        from wexample_prompt.responses.data.properties_prompt_response import PropertiesPromptResponse

        response = PropertiesPromptResponse.create_properties(
            properties=properties,
            title=title,
            nested_indent=nested_indent,
            context=self.create_context(),
            **kwargs
        )

        self.print_response(response)
        return response
