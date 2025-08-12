"""Base class for testing title prompt responses."""
from abc import ABC

from wexample_prompt.tests.abstract_prompt_response_test import AbstractPromptResponseTest


class AbstractTitlePromptResponseTest(AbstractPromptResponseTest, ABC):
    """Base class for testing title prompt responses."""

    def get_expected_lines(self) -> int:
        """Return the expected number of lines in the rendered response."""
        return 3  # Title messages have empty lines before and after

    def test_custom_fill_char(self):
        """Test response with custom fill character."""
        fill_char = "."
        response = self.create_test_response(self.test_message, fill_char=fill_char)
        rendered = response.render()

        self.assert_common_response_structure(rendered)
        self.assert_contains_text(rendered, self.test_message)
        self.assertIn(fill_char, rendered)
