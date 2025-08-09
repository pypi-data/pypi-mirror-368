"""
Comprehensive test suite for setup and configuration functionality.

This module tests the setup_log_file_and_logger function and global state management
in the isolated-logging library, including initialization, file handling, and cleanup.
"""

import os
from unittest.mock import Mock, patch

import pytest

import isolated_logging.functional as functional
from isolated_logging import setup_log_file_and_logger


class TestSetupLogFileAndLogger:
    """Tests for the main setup function and global state management."""

    def test_setup_with_independent_logging_creates_temp_file(self, captured_output):
        """Test that setup with independent logging creates a temporary file."""
        log_file, logger = setup_log_file_and_logger(setup_independent_logging=True)

        assert log_file is not None
        assert hasattr(log_file, "name")
        assert os.path.exists(log_file.name)
        assert log_file.name.endswith(".log")
        assert logger is None

        # Verify log file creation message was printed
        assert any("Log file created at:" in line for line in captured_output)

    def test_setup_with_custom_path_creates_file_at_path(self, temp_log_path, captured_output):
        """Test that setup with custom path creates file at specified location."""
        log_file, logger = setup_log_file_and_logger(
            path=temp_log_path, setup_independent_logging=True
        )

        assert log_file is not None
        assert log_file.name == temp_log_path
        assert os.path.exists(temp_log_path)
        assert logger is None

        # Verify log file creation message
        assert any("Log file created at:" in line for line in captured_output)

    def test_setup_with_logger_only_sets_logger(self, mock_logger):
        """Test that setup with only logger parameter sets the logger."""
        log_file, logger = setup_log_file_and_logger(logger=mock_logger)

        assert log_file is None
        assert logger is mock_logger
        assert functional._logger is mock_logger

    def test_setup_with_both_file_and_logger(self, mock_logger, captured_output):
        """Test setup with both file and logger parameters."""
        log_file, logger = setup_log_file_and_logger(
            logger=mock_logger, setup_independent_logging=True
        )

        assert log_file is not None
        assert logger is mock_logger
        assert functional._logger is mock_logger
        assert os.path.exists(log_file.name)

    def test_setup_without_parameters_shows_warning(self, captured_output):
        """Test that setup without parameters shows appropriate warning."""
        log_file, logger = setup_log_file_and_logger()

        assert log_file is None
        assert logger is None

        # Verify warning message
        assert any("No log file or logger set up!" in line for line in captured_output)

    def test_setup_preserves_existing_log_file(self, temp_log_file, captured_output):
        """Test that subsequent setups preserve existing log file."""
        # Set up initial file
        functional._log_file = temp_log_file

        # Call setup again
        log_file, logger = setup_log_file_and_logger(setup_independent_logging=True)

        # Should return the existing file
        assert log_file is temp_log_file
        assert functional._log_file is temp_log_file

        # Should not create new file message
        assert not any("Log file created at:" in line for line in captured_output)

    def test_setup_preserves_existing_logger(self, mock_logger):
        """Test that subsequent setups preserve existing logger."""
        # Set up initial logger
        functional._logger = mock_logger

        # Call setup with different logger
        new_logger = Mock()
        log_file, logger = setup_log_file_and_logger(logger=new_logger)

        # Should preserve original logger
        assert logger is mock_logger
        assert functional._logger is mock_logger

    @patch("atexit.register")
    def test_setup_registers_cleanup_on_exit(self, mock_atexit):
        """Test that setup registers cleanup function with atexit."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Verify atexit.register was called with close_log
        mock_atexit.assert_called_once_with(functional.close_log)

    def test_setup_handles_file_creation_error(self, monkeypatch):
        """Test that setup handles file creation errors gracefully."""

        # Mock open to raise an exception
        def mock_open(*args, **kwargs):
            raise PermissionError("Permission denied")

        monkeypatch.setattr("builtins.open", mock_open)

        with pytest.raises(PermissionError):
            setup_log_file_and_logger(path="/invalid/path/file.log", setup_independent_logging=True)

    def test_global_state_initialization(self):
        """Test that global state variables are properly initialized."""
        # Check that global variables exist and have correct initial types
        assert hasattr(functional, "_log_file")
        assert hasattr(functional, "_logger")
        assert hasattr(functional, "_function_stats")
        assert hasattr(functional, "_loop_stats")
        assert hasattr(functional, "_checkpoint_stats")

        # After cleanup fixture, these should be in clean state
        assert functional._log_file is None
        assert functional._logger is None
        assert len(functional._function_stats) == 0
        assert len(functional._loop_stats) == 0
        assert len(functional._checkpoint_stats) == 0


class TestCloseLog:
    """Tests for the close_log function."""

    def test_close_log_with_open_file(self, temp_log_file):
        """Test that close_log properly closes an open file."""
        functional._log_file = temp_log_file

        functional.close_log()

        assert functional._log_file is None
        assert temp_log_file.closed

    def test_close_log_with_no_file(self):
        """Test that close_log handles the case when no file is open."""
        functional._log_file = None

        # Should not raise an exception
        functional.close_log()

        assert functional._log_file is None

    def test_close_log_with_already_closed_file(self, temp_log_file):
        """Test that close_log handles already closed files."""
        temp_log_file.close()  # Close it first
        functional._log_file = temp_log_file

        # Should not raise an exception
        functional.close_log()

        assert functional._log_file is None


class TestReadLog:
    """Tests for the read_log function."""

    def test_read_log_with_content(self):
        """Test reading log content from file."""
        # Setup log file with content
        setup_log_file_and_logger(setup_independent_logging=True)
        test_content = "Test log content\nSecond line\n"

        # Write content to log file
        functional._log_file.write(test_content)
        functional._log_file.flush()

        # Read content back
        content = functional.read_log()

        assert content == test_content

    def test_read_log_empty_file(self):
        """Test reading from empty log file."""
        setup_log_file_and_logger(setup_independent_logging=True)

        content = functional.read_log()

        assert content == ""

    def test_read_log_no_file_setup(self):
        """Test reading log when no file is set up."""
        content = functional.read_log()

        assert content == ""

    def test_read_log_with_unicode_content(self):
        """Test reading log file with unicode content."""
        setup_log_file_and_logger(setup_independent_logging=True)
        unicode_content = "Test with unicode: 你好 🌟 café\n"

        functional._log_file.write(unicode_content)
        functional._log_file.flush()

        content = functional.read_log()

        assert content == unicode_content


class TestCleanupLog:
    """Tests for the cleanup_log function."""

    def test_cleanup_log_removes_file(self):
        """Test that cleanup_log removes the log file from filesystem."""
        setup_log_file_and_logger(setup_independent_logging=True)
        log_path = functional._log_file.name

        # Verify file exists
        assert os.path.exists(log_path)

        functional.cleanup_log()

        # Verify file is removed and global state is cleared
        assert not os.path.exists(log_path)
        assert functional._log_file is None

    def test_cleanup_log_no_file(self):
        """Test that cleanup_log handles case when no file exists."""
        functional._log_file = None

        # Should not raise an exception
        functional.cleanup_log()

        assert functional._log_file is None

    def test_cleanup_log_file_already_removed(self, temp_log_file):
        """Test cleanup when file has already been removed externally."""
        functional._log_file = temp_log_file
        file_path = temp_log_file.name
        temp_log_file.close()

        # Remove file externally
        if os.path.exists(file_path):
            os.unlink(file_path)

        # Should handle missing file gracefully
        functional.cleanup_log()

        assert functional._log_file is None


class TestGlobalStateManagement:
    """Tests for global state management and thread safety."""

    def test_function_stats_isolation(self):
        """Test that function stats are properly isolated between tests."""
        # Add some stats
        functional._function_stats["test_func"].append(1.5)
        functional._function_stats["test_func"].append(2.0)

        assert len(functional._function_stats["test_func"]) == 2
        assert functional._function_stats["test_func"] == [1.5, 2.0]

    def test_loop_stats_isolation(self):
        """Test that loop stats are properly isolated between tests."""
        loop_id = "test_loop"
        functional._loop_stats[loop_id]["times"].append(1.0)
        functional._loop_stats[loop_id]["iterations"] = 5

        assert len(functional._loop_stats[loop_id]["times"]) == 1
        assert functional._loop_stats[loop_id]["iterations"] == 5

    def test_checkpoint_stats_isolation(self):
        """Test that checkpoint stats are properly isolated between tests."""
        checkpoint_id = "test_checkpoint"
        functional._checkpoint_stats[checkpoint_id]["times"].append(2.5)
        functional._checkpoint_stats[checkpoint_id]["last_checkpoint"] = 1000.0

        assert len(functional._checkpoint_stats[checkpoint_id]["times"]) == 1
        assert functional._checkpoint_stats[checkpoint_id]["last_checkpoint"] == 1000.0

    def test_multiple_setups_same_test(self):
        """Test multiple setup calls within the same test."""
        # First setup
        log_file1, logger1 = setup_log_file_and_logger(setup_independent_logging=True)

        # Second setup - should reuse existing
        log_file2, logger2 = setup_log_file_and_logger(setup_independent_logging=True)

        assert log_file1 is log_file2
        assert logger1 is logger2

    def test_global_state_persistence_during_test(self):
        """Test that global state persists during a single test execution."""
        # Set up some state
        functional._function_stats["func1"].append(1.0)
        setup_log_file_and_logger(setup_independent_logging=True)

        # Verify state persists
        assert len(functional._function_stats["func1"]) == 1
        assert functional._log_file is not None

        # Add more state
        functional._function_stats["func2"].append(2.0)

        # Verify all state is still there
        assert len(functional._function_stats["func1"]) == 1
        assert len(functional._function_stats["func2"]) == 1
        assert functional._log_file is not None
