"""
Comprehensive test suite for utility functions.

This module tests utility functions including the color system, log_message functions,
log_list_elements, and internal logging mechanisms in the isolated-logging library.
"""

from unittest.mock import patch

import pytest

import isolated_logging.functional as functional
from isolated_logging import (
    log_list_elements,
    log_message,
    log_message_with_color,
    setup_log_file_and_logger,
)
from isolated_logging.functional import Color


class TestColorEnum:
    """Tests for the Color enum and ANSI escape codes."""

    def test_color_enum_values(self):
        """Test that all color enum values are correct ANSI escape codes."""
        expected_colors = {
            "RESET": "\033[0m",
            "BLUE": "\033[94m",
            "GREEN": "\033[92m",
            "YELLOW": "\033[93m",
            "RED": "\033[91m",
            "CYAN": "\033[96m",
            "GRAY": "\033[90m",
            "PURPLE": "\033[95m",
            "DULL": "\033[37m",
            "ORANGE": "\033[38;5;214m",
        }

        for color_name, expected_code in expected_colors.items():
            color_enum = getattr(Color, color_name)
            assert color_enum.value == expected_code

    def test_color_enum_completeness(self):
        """Test that all expected colors are present in the enum."""
        expected_color_names = {
            "RESET",
            "BLUE",
            "GREEN",
            "YELLOW",
            "RED",
            "CYAN",
            "GRAY",
            "PURPLE",
            "DULL",
            "ORANGE",
        }

        actual_color_names = {color.name for color in Color}
        assert actual_color_names == expected_color_names

    def test_color_enum_accessibility(self):
        """Test that colors can be accessed by name and attribute."""
        # Test attribute access
        assert Color.BLUE.value == "\033[94m"
        assert Color.RED.value == "\033[91m"

        # Test name-based access
        assert Color["BLUE"].value == "\033[94m"
        assert Color["RED"].value == "\033[91m"

    def test_color_string_representation(self):
        """Test that colors have proper string representations."""
        assert str(Color.BLUE) == "Color.BLUE"
        assert repr(Color.BLUE) == "<Color.BLUE: '\\x1b[94m'>"


class TestLogMessage:
    """Tests for the basic log_message function."""

    def test_log_message_basic_functionality(self):
        """Test that log_message writes to log file."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_message("Test message")

        log_content = functional.read_log()
        assert "Test message" in log_content

    def test_log_message_uses_blue_color(self):
        """Test that log_message uses blue color by default."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_message("Blue message")

        log_content = functional.read_log()
        assert Color.BLUE.value in log_content
        assert Color.RESET.value in log_content

    def test_log_message_multiple_calls(self):
        """Test multiple log_message calls."""
        setup_log_file_and_logger(setup_independent_logging=True)

        messages = ["Message 1", "Message 2", "Message 3"]
        for message in messages:
            log_message(message)

        log_content = functional.read_log()
        for message in messages:
            assert message in log_content

    def test_log_message_with_special_characters(self):
        """Test log_message with special characters."""
        setup_log_file_and_logger(setup_independent_logging=True)

        special_message = "Special chars: @#$%^&*()_+-=[]{}|;':\",./<>?`~"
        log_message(special_message)

        log_content = functional.read_log()
        assert special_message in log_content

    def test_log_message_with_unicode(self):
        """Test log_message with unicode characters."""
        setup_log_file_and_logger(setup_independent_logging=True)

        unicode_message = "Unicode test: 你好 🌟 café émojis 🚀"
        log_message(unicode_message)

        log_content = functional.read_log()
        assert unicode_message in log_content

    def test_log_message_with_external_logger(self, mock_logger):
        """Test log_message integration with external logger."""
        setup_log_file_and_logger(logger=mock_logger)

        log_message("External logger test")

        # Verify external logger was called
        mock_logger.info.assert_called()

        # Check that the colored message was passed to logger
        call_args = mock_logger.info.call_args[0][0]
        assert "External logger test" in call_args
        assert Color.BLUE.value in call_args

    def test_log_message_without_setup(self, captured_output):
        """Test log_message behavior when no logging is set up."""
        log_message("No setup message")

        # Should show warning about no logging setup
        assert any("No log file or logger set up!" in line for line in captured_output)


class TestLogMessageWithColor:
    """Tests for the log_message_with_color function."""

    def test_log_message_with_different_colors(self):
        """Test log_message_with_color with different color options."""
        setup_log_file_and_logger(setup_independent_logging=True)

        color_tests = [
            ("Red message", Color.RED),
            ("Green message", Color.GREEN),
            ("Yellow message", Color.YELLOW),
            ("Cyan message", Color.CYAN),
            ("Purple message", Color.PURPLE),
        ]

        for message, color in color_tests:
            log_message_with_color(message, color)

        log_content = functional.read_log()

        for message, color in color_tests:
            assert message in log_content
            assert color.value in log_content

        # Should have multiple reset codes
        reset_count = log_content.count(Color.RESET.value)
        assert reset_count == len(color_tests)

    def test_color_wrapping(self):
        """Test that messages are properly wrapped with color codes."""
        setup_log_file_and_logger(setup_independent_logging=True)

        message = "Wrapped message"
        log_message_with_color(message, Color.GREEN)

        log_content = functional.read_log()

        # Should contain the message wrapped in color codes
        expected_pattern = f"{Color.GREEN.value}{message}{Color.RESET.value}"
        assert expected_pattern in log_content

    def test_color_message_isolation(self):
        """Test that color codes don't bleed between messages."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_message_with_color("Message 1", Color.RED)
        log_message_with_color("Message 2", Color.BLUE)

        log_content = functional.read_log()

        # Each message should be properly reset
        lines = log_content.split("\n")
        red_line = next(line for line in lines if "Message 1" in line)
        blue_line = next(line for line in lines if "Message 2" in line)

        assert Color.RED.value in red_line
        assert Color.RESET.value in red_line
        assert Color.BLUE.value in blue_line
        assert Color.RESET.value in blue_line

    def test_all_colors_work(self):
        """Test that all colors in the enum work correctly."""
        setup_log_file_and_logger(setup_independent_logging=True)

        for color in Color:
            if color != Color.RESET:  # Skip RESET as it's not a display color
                message = f"Testing {color.name} color"
                log_message_with_color(message, color)

        log_content = functional.read_log()

        # Should contain all color codes
        for color in Color:
            if color != Color.RESET:
                assert color.value in log_content

    def test_empty_message_with_color(self):
        """Test log_message_with_color with empty message."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_message_with_color("", Color.GREEN)

        log_content = functional.read_log()

        # Should still contain color codes even with empty message
        assert Color.GREEN.value in log_content
        assert Color.RESET.value in log_content

    def test_color_with_external_logger(self, mock_logger):
        """Test log_message_with_color with external logger."""
        setup_log_file_and_logger(logger=mock_logger)

        log_message_with_color("Colored external message", Color.YELLOW)

        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "Colored external message" in call_args
        assert Color.YELLOW.value in call_args
        assert Color.RESET.value in call_args


class TestLogListElements:
    """Tests for the log_list_elements function."""

    def test_log_list_elements_basic(self):
        """Test logging a basic list of elements."""
        setup_log_file_and_logger(setup_independent_logging=True)

        test_list = ["item1", "item2", "item3"]
        log_list_elements(test_list)

        log_content = functional.read_log()

        # Should contain header
        assert "Logging list elements:" in log_content

        # Should contain each item with bullet point
        for item in test_list:
            assert f"- {item}" in log_content

    def test_log_list_elements_different_types(self):
        """Test logging list with different data types."""
        setup_log_file_and_logger(setup_independent_logging=True)

        mixed_list = [1, "string", 3.14, True, None, [1, 2, 3]]
        log_list_elements(mixed_list)

        log_content = functional.read_log()

        assert "- 1" in log_content
        assert "- string" in log_content
        assert "- 3.14" in log_content
        assert "- True" in log_content
        assert "- None" in log_content
        assert "- [1, 2, 3]" in log_content

    def test_log_list_elements_empty_list(self):
        """Test logging an empty list."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_list_elements([])

        log_content = functional.read_log()

        # Should have header but no items
        assert "Logging list elements:" in log_content
        # Count of "-" should be minimal (only from color codes if any)
        content_lines = [line for line in log_content.split("\n") if line.strip()]
        item_lines = [line for line in content_lines if line.strip().startswith("- ")]
        assert len(item_lines) == 0

    def test_log_list_elements_single_item(self):
        """Test logging a list with single item."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_list_elements(["single_item"])

        log_content = functional.read_log()

        assert "Logging list elements:" in log_content
        assert "- single_item" in log_content

    def test_log_list_elements_colors(self):
        """Test that log_list_elements uses correct colors."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_list_elements(["test"])

        log_content = functional.read_log()

        # Header should be green
        assert Color.GREEN.value in log_content
        # Items should be blue
        assert Color.BLUE.value in log_content
        # Should have reset codes
        assert Color.RESET.value in log_content

    def test_log_list_elements_with_complex_objects(self):
        """Test logging list with complex objects."""
        setup_log_file_and_logger(setup_independent_logging=True)

        complex_list = [
            {"name": "object1", "value": 42},
            {"name": "object2", "data": [1, 2, 3]},
        ]
        log_list_elements(complex_list)

        log_content = functional.read_log()

        # Should contain string representation of objects
        assert "- {'name': 'object1', 'value': 42}" in log_content
        assert "- {'name': 'object2', 'data': [1, 2, 3]}" in log_content

    def test_log_list_elements_with_unicode(self):
        """Test logging list with unicode elements."""
        setup_log_file_and_logger(setup_independent_logging=True)

        unicode_list = ["regular", "unicode: 你好", "emoji: 🚀", "café"]
        log_list_elements(unicode_list)

        log_content = functional.read_log()

        for item in unicode_list:
            assert f"- {item}" in log_content

    def test_log_list_elements_large_list(self):
        """Test logging a large list."""
        setup_log_file_and_logger(setup_independent_logging=True)

        large_list = [f"item_{i}" for i in range(100)]
        log_list_elements(large_list)

        log_content = functional.read_log()

        # Should contain all items
        for i in range(100):
            assert f"- item_{i}" in log_content

        # Should have the correct number of bullet points
        bullet_count = log_content.count("- item_")
        assert bullet_count == 100

    def test_log_list_elements_with_external_logger(self, mock_logger):
        """Test log_list_elements with external logger."""
        setup_log_file_and_logger(logger=mock_logger)

        log_list_elements(["external", "test"])

        # Should call external logger multiple times (header + items)
        assert mock_logger.info.call_count >= 3


class TestInternalLoggingMechanism:
    """Tests for the internal _log_raw_message function."""

    def test_log_raw_message_to_file(self):
        """Test _log_raw_message writes directly to file."""
        setup_log_file_and_logger(setup_independent_logging=True)

        functional._log_raw_message("Raw message test")

        log_content = functional.read_log()
        assert "Raw message test" in log_content

    def test_log_raw_message_to_external_logger(self, mock_logger):
        """Test _log_raw_message sends to external logger."""
        setup_log_file_and_logger(logger=mock_logger)

        functional._log_raw_message("External raw message")

        mock_logger.info.assert_called_with("External raw message")

    def test_log_raw_message_to_both(self, mock_logger):
        """Test _log_raw_message writes to both file and external logger."""
        setup_log_file_and_logger(setup_independent_logging=True, logger=mock_logger)

        functional._log_raw_message("Both destinations")

        # Should be in file
        log_content = functional.read_log()
        assert "Both destinations" in log_content

        # Should be sent to external logger
        mock_logger.info.assert_called_with("Both destinations")

    def test_log_raw_message_with_custom_ending(self):
        """Test _log_raw_message with custom line ending."""
        setup_log_file_and_logger(setup_independent_logging=True)

        functional._log_raw_message("Custom ending", end="***")

        log_content = functional.read_log()
        assert "Custom ending***" in log_content

    def test_log_raw_message_file_flushing(self):
        """Test that _log_raw_message flushes file buffer."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Mock the flush method to verify it's called
        original_flush = functional._log_file.flush
        flush_called = False

        def mock_flush():
            nonlocal flush_called
            flush_called = True
            original_flush()

        functional._log_file.flush = mock_flush

        functional._log_raw_message("Flush test")

        assert flush_called

        # Restore original method
        functional._log_file.flush = original_flush

    def test_log_raw_message_calls_setup(self):
        """Test that _log_raw_message calls setup function."""
        # Don't set up logging initially

        with patch("isolated_logging.functional.setup_log_file_and_logger") as mock_setup:
            mock_setup.return_value = (None, None)  # No logging available

            functional._log_raw_message("Setup test")

            # Verify setup was called
            mock_setup.assert_called_once()


class TestUtilityFunctionIntegration:
    """Tests for integration between utility functions."""

    def test_message_functions_work_together(self):
        """Test that different message functions work together correctly."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_message("Regular blue message")
        log_message_with_color("Custom red message", Color.RED)
        log_list_elements(["list", "item"])

        log_content = functional.read_log()

        # Should contain all messages with appropriate colors
        assert "Regular blue message" in log_content
        assert "Custom red message" in log_content
        assert "Logging list elements:" in log_content
        assert "- list" in log_content
        assert "- item" in log_content

        # Should contain multiple color codes
        assert Color.BLUE.value in log_content
        assert Color.RED.value in log_content
        assert Color.GREEN.value in log_content

    def test_utility_functions_preserve_order(self):
        """Test that utility function calls preserve message order."""
        setup_log_file_and_logger(setup_independent_logging=True)

        messages_and_calls = [
            ("First", lambda: log_message("First")),
            ("Second", lambda: log_message_with_color("Second", Color.YELLOW)),
            ("Third", lambda: log_message("Third")),
        ]

        for _, call_func in messages_and_calls:
            call_func()

        log_content = functional.read_log()
        lines = [line for line in log_content.split("\n") if line.strip()]

        # Extract actual message content (removing color codes for comparison)
        cleaned_lines = []
        for line in lines:
            # Remove ANSI color codes for content comparison
            import re

            cleaned = re.sub(r"\033\[[0-9;]*m", "", line)
            cleaned_lines.append(cleaned.strip())

        # Find our messages in the cleaned content
        message_positions = {}
        for i, cleaned_line in enumerate(cleaned_lines):
            for msg, _ in messages_and_calls:
                if msg in cleaned_line:
                    message_positions[msg] = i
                    break

        # Verify order is preserved
        assert message_positions["First"] < message_positions["Second"]
        assert message_positions["Second"] < message_positions["Third"]

    def test_utility_functions_error_handling(self):
        """Test that utility functions handle errors gracefully."""
        # Test with no logging setup
        with patch("isolated_logging.functional.setup_log_file_and_logger") as mock_setup:
            mock_setup.return_value = (None, None)  # No logging available

            # Should not raise exceptions
            log_message("Error test")
            log_message_with_color("Error test", Color.RED)
            log_list_elements(["error", "test"])

    def test_utility_functions_with_file_errors(self):
        """Test utility functions when file operations fail."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Mock file write to raise an exception
        original_write = functional._log_file.write

        def failing_write(content):
            raise OSError("Disk full")

        functional._log_file.write = failing_write

        # Should handle file write errors gracefully
        with pytest.raises(IOError):
            log_message("This should fail")

        # Restore original method
        functional._log_file.write = original_write


class TestUtilityFunctionPerformance:
    """Tests for utility function performance characteristics."""

    def test_large_message_handling(self):
        """Test utility functions with very large messages."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Create a large message (1MB)
        large_message = "A" * (1024 * 1024)

        log_message_with_color(large_message, Color.BLUE)

        log_content = functional.read_log()
        assert large_message in log_content

    def test_many_small_messages_performance(self):
        """Test performance with many small messages."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Log many small messages
        for i in range(1000):
            log_message(f"Message {i}")

        log_content = functional.read_log()

        # Verify all messages are present
        assert "Message 0" in log_content
        assert "Message 999" in log_content

        # Count total messages
        message_count = log_content.count("Message ")
        assert message_count == 1000

    def test_mixed_function_calls_performance(self):
        """Test performance with mixed utility function calls."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Mix different types of logging calls
        for i in range(100):
            log_message(f"Regular {i}")
            log_message_with_color(f"Colored {i}", Color.GREEN)
            if i % 10 == 0:
                log_list_elements([f"list_{i}", f"item_{i}"])

        log_content = functional.read_log()

        # Should contain all types of messages
        assert "Regular 50" in log_content
        assert "Colored 50" in log_content
        assert "- list_50" in log_content
