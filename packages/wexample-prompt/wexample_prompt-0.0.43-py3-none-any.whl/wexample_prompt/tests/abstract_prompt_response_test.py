"""Base class for testing prompt responses."""
import unittest
from abc import ABC, abstractmethod
from typing import Type
from unittest.mock import patch

from wexample_prompt.common.io_manager import IoManager
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.example.example_class_with_context import ExampleClassWithContext
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse


class AbstractPromptResponseTest(unittest.TestCase, ABC):
    """Base class for testing prompt responses.
    
    This class provides common functionality for testing prompt responses at three levels:
    1. Response class behavior
    2. IoManager integration
    3. PromptContext implementation
    """

    def setUp(self):
        """Set up common test fixtures."""
        self.terminal_width = 80
        self.context = PromptContext(terminal_width=self.terminal_width)
        self.io_manager = IoManager(terminal_width=self.terminal_width)
        self.test_message = "Test message"

    @abstractmethod
    def get_expected_lines(self) -> int:
        """Return the expected number of lines in the rendered response."""
        pass

    def assert_common_response_structure(self, rendered: str):
        """Assert common structure for rendered responses."""
        lines = rendered.split("\n")
        expected_lines = self.get_expected_lines()
        self.assertEqual(len(lines), expected_lines)

        # If more than one line, first and last should be empty
        if expected_lines > 1:
            self.assertEqual(lines[0].strip(), "")
            self.assertEqual(lines[-1].strip(), "")

    def assert_contains_text(self, rendered: str, text: str):
        """Assert that rendered output contains specific text."""
        self.assertIn(text, rendered)

    @patch('wexample_prompt.common.color_manager.ColorManager.supports_color')
    def create_colored_test_context(self, mock_supports_color, color_enabled: bool = True):
        """Create a test context with color support controlled."""
        mock_supports_color.return_value = color_enabled
        return self.context

    @abstractmethod
    def get_response_class(self) -> Type[AbstractPromptResponse]:
        """Return the response class to test."""
        pass

    @abstractmethod
    def create_test_response(self, text: str, **kwargs) -> AbstractPromptResponse:
        """Create a response instance."""
        pass

    @abstractmethod
    def get_io_method_name(self) -> str:
        """Return the name of the IoManager method for this response type."""
        pass

    @abstractmethod
    def _assert_specific_format(self, rendered: str):
        """Assert format specific to this response type."""
        pass

    def test_response_class(self):
        """Test response class behavior."""
        response = self.create_test_response(self.test_message)
        rendered = response.render()

        self.assert_common_response_structure(rendered)
        self.assert_contains_text(rendered, self.test_message)
        self._assert_specific_format(rendered)

    def test_io_manager(self):
        """Test IoManager integration."""
        method = getattr(self.io_manager, self.get_io_method_name())
        response = method(self.test_message)
        rendered = response.render()

        self.assert_common_response_structure(rendered)
        self.assert_contains_text(rendered, self.test_message)
        self._assert_specific_format(rendered)

    def test_prompt_context(self):
        """Test PromptContext implementation."""
        context = self.context
        class_with_context = ExampleClassWithContext(
            context=context,
            io_manager=self.io_manager
        )
        method = getattr(class_with_context, self.get_io_method_name())
        response = method(self.test_message)
        rendered = response.render()

        self.assert_common_response_structure(rendered)
        self.assert_contains_text(rendered, self.test_message)
        self._assert_specific_format(rendered)

    @patch('wexample_prompt.common.color_manager.ColorManager.supports_color')
    def test_custom_color(self, mock_supports_color):
        """Test response with custom color."""
        context = self.create_colored_test_context(mock_supports_color)
        from wexample_prompt.enums.terminal_color import TerminalColor

        response = self.create_test_response(self.test_message, context=context, color=TerminalColor.GREEN)
        rendered = response.render()

        self.assert_common_response_structure(rendered)
        self.assert_contains_text(rendered, self.test_message)
        self._assert_specific_format(rendered)

    def test_no_color(self):
        """Test response without color."""
        response = self.create_test_response(self.test_message, color=None)
        rendered = response.render()

        self.assert_common_response_structure(rendered)
        self.assert_contains_text(rendered, self.test_message)
        self.assertNotIn("\033[", rendered)  # No ANSI color codes
