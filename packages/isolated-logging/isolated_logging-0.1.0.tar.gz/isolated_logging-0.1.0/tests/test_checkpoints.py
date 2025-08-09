"""
Comprehensive test suite for checkpoint functionality.

This module tests the log_checkpoint function including timing measurements,
statistics tracking, custom messages, and integration with the logging system.
"""

import time
from unittest.mock import patch

import pytest

import isolated_logging.functional as functional
from isolated_logging import log_checkpoint, setup_log_file_and_logger


class TestLogCheckpointBasicFunctionality:
    """Tests for basic checkpoint functionality."""

    def test_first_checkpoint_creation(self):
        """Test creating the first checkpoint for an ID."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_checkpoint("test_checkpoint")

        # Check that checkpoint was recorded
        assert "test_checkpoint" in functional._checkpoint_stats
        stats = functional._checkpoint_stats["test_checkpoint"]
        assert "last_checkpoint" in stats
        assert "times" in stats
        assert stats["last_checkpoint"] is not None
        assert len(stats["times"]) == 0  # No elapsed time for first checkpoint

    @patch("time.time")
    def test_second_checkpoint_measures_elapsed_time(self, mock_time):
        """Test that second checkpoint measures time since first."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_time.side_effect = [1000.0, 1005.0]  # 5 second difference

        log_checkpoint("test_checkpoint")
        log_checkpoint("test_checkpoint")

        stats = functional._checkpoint_stats["test_checkpoint"]
        assert len(stats["times"]) == 1
        assert stats["times"][0] == 5.0

    @patch("time.time")
    def test_multiple_checkpoints_accumulate_times(self, mock_time):
        """Test that multiple checkpoints accumulate timing data."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_time.side_effect = [1000.0, 1003.0, 1007.0, 1012.0]  # 3, 4, 5 second intervals

        log_checkpoint("test_checkpoint")  # Initial
        log_checkpoint("test_checkpoint")  # +3 seconds
        log_checkpoint("test_checkpoint")  # +4 seconds
        log_checkpoint("test_checkpoint")  # +5 seconds

        stats = functional._checkpoint_stats["test_checkpoint"]
        assert len(stats["times"]) == 3
        assert stats["times"][0] == 3.0
        assert stats["times"][1] == 4.0
        assert stats["times"][2] == 5.0

    def test_different_checkpoint_ids_isolated(self):
        """Test that different checkpoint IDs maintain separate statistics."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_checkpoint("checkpoint_a")
        log_checkpoint("checkpoint_b")

        assert "checkpoint_a" in functional._checkpoint_stats
        assert "checkpoint_b" in functional._checkpoint_stats

        # Should have separate state
        assert (
            functional._checkpoint_stats["checkpoint_a"]["last_checkpoint"]
            != functional._checkpoint_stats["checkpoint_b"]["last_checkpoint"]
        )


class TestCheckpointCustomMessages:
    """Tests for checkpoint custom message functionality."""

    def test_checkpoint_with_custom_message(self):
        """Test checkpoint with custom message."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_checkpoint("test_checkpoint", "Starting data processing")

        log_content = functional.read_log()
        assert "Checkpoint test_checkpoint: Starting data processing" in log_content

    def test_checkpoint_without_custom_message(self):
        """Test checkpoint without custom message."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_checkpoint("test_checkpoint")

        log_content = functional.read_log()
        # Should not contain custom message, but should have initial checkpoint message
        assert "Initial checkpoint recorded" in log_content

    def test_multiple_checkpoints_with_different_messages(self):
        """Test multiple checkpoints with different custom messages."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_checkpoint("process", "Phase 1 started")
        log_checkpoint("process", "Phase 2 started")
        log_checkpoint("process", "Phase 3 started")

        log_content = functional.read_log()
        assert "Checkpoint process: Phase 1 started" in log_content
        assert "Checkpoint process: Phase 2 started" in log_content
        assert "Checkpoint process: Phase 3 started" in log_content

    def test_checkpoint_message_with_special_characters(self):
        """Test checkpoint with special characters in message."""
        setup_log_file_and_logger(setup_independent_logging=True)

        special_message = "Processing file: data_2024-01-15.json (50% complete) 🚀"
        log_checkpoint("file_processing", special_message)

        log_content = functional.read_log()
        assert special_message in log_content


class TestCheckpointLogging:
    """Tests for checkpoint logging functionality."""

    def test_initial_checkpoint_logging(self):
        """Test that initial checkpoint is logged correctly."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_checkpoint("first_time")

        log_content = functional.read_log()
        assert "Checkpoint first_time: Initial checkpoint recorded" in log_content

    @patch("time.time")
    def test_elapsed_time_logging(self, mock_time):
        """Test that elapsed time is logged correctly."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_time.side_effect = [1000.0, 1002.5]  # 2.5 second elapsed

        log_checkpoint("timing_test")
        log_checkpoint("timing_test")

        log_content = functional.read_log()
        assert "Elapsed time since last checkpoint: 2.50 seconds" in log_content

    @patch("numpy.mean")
    @patch("numpy.std")
    def test_statistics_logging(self, mock_std, mock_mean):
        """Test that checkpoint statistics are logged."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_mean.return_value = 3.5
        mock_std.return_value = 1.2

        # Create some checkpoint timing data
        functional._checkpoint_stats["stats_test"]["times"] = [2.0, 3.0, 5.0]
        functional._checkpoint_stats["stats_test"]["last_checkpoint"] = 1000.0

        log_checkpoint("stats_test")

        log_content = functional.read_log()
        assert "Avg time: 3.50 seconds" in log_content
        assert "Std dev: 1.20" in log_content
        assert "Total checks: 4" in log_content

        # Verify numpy functions were called
        mock_mean.assert_called_once()
        mock_std.assert_called_once()

    def test_statistics_with_single_measurement(self):
        """Test statistics logging with only one measurement."""
        setup_log_file_and_logger(setup_independent_logging=True)

        with patch("time.time", side_effect=[1000.0, 1003.0]):
            log_checkpoint("single_measurement")
            log_checkpoint("single_measurement")

        log_content = functional.read_log()
        # Should handle single measurement case (std dev = 0)
        assert "Avg time:" in log_content
        assert "Std dev: 0.00" in log_content
        assert "Total checks: 1" in log_content

    def test_no_statistics_for_initial_checkpoint(self):
        """Test that initial checkpoint doesn't log statistics."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_checkpoint("initial_only")

        log_content = functional.read_log()
        assert "Initial checkpoint recorded" in log_content
        assert "Avg time:" not in log_content
        assert "Std dev:" not in log_content


class TestCheckpointStatisticsCalculation:
    """Tests for checkpoint statistics calculation."""

    @patch("time.time")
    def test_average_time_calculation(self, mock_time):
        """Test that average checkpoint time is calculated correctly."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_time.side_effect = [1000.0, 1002.0, 1005.0, 1009.0]  # 2, 3, 4 second intervals

        log_checkpoint("avg_test")
        log_checkpoint("avg_test")  # 2 seconds
        log_checkpoint("avg_test")  # 3 seconds
        log_checkpoint("avg_test")  # 4 seconds

        stats = functional._checkpoint_stats["avg_test"]
        times = stats["times"]
        assert len(times) == 3
        assert times == [2.0, 3.0, 4.0]

        # Average should be 3.0
        log_content = functional.read_log()
        assert "Avg time: 3.00 seconds" in log_content

    @patch("time.time")
    def test_standard_deviation_calculation(self, mock_time):
        """Test that standard deviation is calculated correctly."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_time.side_effect = [1000.0, 1001.0, 1003.0]  # 1, 2 second intervals

        log_checkpoint("std_test")
        log_checkpoint("std_test")  # 1 second
        log_checkpoint("std_test")  # 2 seconds

        log_content = functional.read_log()
        # Should calculate std dev for [1.0, 2.0]
        assert "Std dev:" in log_content

    def test_statistics_isolation_between_checkpoints(self):
        """Test that statistics are isolated between different checkpoint IDs."""
        setup_log_file_and_logger(setup_independent_logging=True)

        with patch("time.time", side_effect=[1000.0, 1002.0, 1010.0, 1013.0]):
            log_checkpoint("checkpoint_1")
            log_checkpoint("checkpoint_1")  # 2 seconds

            log_checkpoint("checkpoint_2")
            log_checkpoint("checkpoint_2")  # 3 seconds

        stats_1 = functional._checkpoint_stats["checkpoint_1"]
        stats_2 = functional._checkpoint_stats["checkpoint_2"]

        assert stats_1["times"] == [2.0]
        assert stats_2["times"] == [3.0]
        assert stats_1["times"] != stats_2["times"]

    def test_checkpoint_count_accuracy(self):
        """Test that checkpoint count is accurate."""
        setup_log_file_and_logger(setup_independent_logging=True)

        with patch("time.time", side_effect=[1000.0, 1001.0, 1002.0, 1003.0, 1004.0]):
            log_checkpoint("count_test")
            log_checkpoint("count_test")  # 1st measurement
            log_checkpoint("count_test")  # 2nd measurement
            log_checkpoint("count_test")  # 3rd measurement
            log_checkpoint("count_test")  # 4th measurement

        log_content = functional.read_log()
        # Should show 4 total checks
        assert "Total checks: 4" in log_content


class TestCheckpointIntegrationWithLogging:
    """Tests for checkpoint integration with logging system."""

    def test_checkpoint_with_external_logger(self, mock_logger):
        """Test checkpoint integration with external logger."""
        setup_log_file_and_logger(logger=mock_logger)

        log_checkpoint("external_logger_test", "Test message")

        # Verify external logger was called
        assert mock_logger.info.call_count >= 1

        # Check that our log messages were sent to external logger
        call_args = [call[0][0] for call in mock_logger.info.call_args_list]
        messages = " ".join(call_args)
        assert "Test message" in messages

    def test_checkpoint_without_logging_setup(self, captured_output):
        """Test checkpoint behavior when no logging is set up."""
        # Don't call setup_log_file_and_logger

        log_checkpoint("no_setup_test")

        # Should show warning about no logging setup
        assert any("No log file or logger set up!" in line for line in captured_output)

    def test_checkpoint_logs_use_correct_colors(self):
        """Test that checkpoint logs use appropriate color coding."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_checkpoint("color_test", "Custom message")

        with patch("time.time", side_effect=[1005.0]):
            log_checkpoint("color_test")  # Second checkpoint

        log_content = functional.read_log()

        # Should contain ANSI color codes
        assert "\033[96m" in log_content  # CYAN color for custom message
        assert "\033[95m" in log_content  # PURPLE color for timing
        assert "\033[37m" in log_content  # DULL color for statistics
        assert "\033[0m" in log_content  # RESET color


class TestCheckpointEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_checkpoint_with_empty_id(self):
        """Test checkpoint with empty string ID."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_checkpoint("")

        # Should work with empty string as ID
        assert "" in functional._checkpoint_stats

        log_content = functional.read_log()
        assert "Checkpoint : Initial checkpoint recorded" in log_content

    def test_checkpoint_with_none_id(self):
        """Test checkpoint with None as ID (should raise error)."""
        setup_log_file_and_logger(setup_independent_logging=True)

        with pytest.raises(TypeError):
            log_checkpoint(None)

    def test_checkpoint_with_numeric_id(self):
        """Test checkpoint with numeric ID."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_checkpoint("123")
        log_checkpoint("123")

        # Should work with string representation of numbers
        assert "123" in functional._checkpoint_stats

    def test_checkpoint_with_very_long_id(self):
        """Test checkpoint with very long ID."""
        setup_log_file_and_logger(setup_independent_logging=True)

        long_id = "a" * 1000  # 1000 character ID
        log_checkpoint(long_id)

        assert long_id in functional._checkpoint_stats

    def test_checkpoint_with_unicode_characters(self):
        """Test checkpoint with unicode characters in ID and message."""
        setup_log_file_and_logger(setup_independent_logging=True)

        unicode_id = "测试_checkpoint_🚀"
        unicode_message = "Processing 数据 with émojis 🎉"

        log_checkpoint(unicode_id, unicode_message)

        assert unicode_id in functional._checkpoint_stats

        log_content = functional.read_log()
        assert unicode_message in log_content

    @patch("time.time")
    def test_checkpoint_with_zero_elapsed_time(self, mock_time):
        """Test checkpoint when no time has elapsed."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_time.return_value = 1000.0  # Same time for both calls

        log_checkpoint("zero_time")
        log_checkpoint("zero_time")

        stats = functional._checkpoint_stats["zero_time"]
        assert stats["times"][0] == 0.0

        log_content = functional.read_log()
        assert "Elapsed time since last checkpoint: 0.00 seconds" in log_content

    @patch("time.time")
    def test_checkpoint_with_negative_time_difference(self, mock_time):
        """Test checkpoint when system time goes backwards."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_time.side_effect = [1000.0, 999.0]  # Time goes backwards

        log_checkpoint("negative_time")
        log_checkpoint("negative_time")

        stats = functional._checkpoint_stats["negative_time"]
        assert stats["times"][0] == -1.0  # Should record the negative time

        log_content = functional.read_log()
        assert "Elapsed time since last checkpoint: -1.00 seconds" in log_content

    def test_many_checkpoints_performance(self):
        """Test performance with many checkpoint calls."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Create many checkpoints quickly
        for _ in range(100):
            log_checkpoint("performance_test")
            time.sleep(0.001)  # Small delay

        stats = functional._checkpoint_stats["performance_test"]
        assert len(stats["times"]) == 99  # 100 calls = 99 measurements

        # Should complete without performance issues


class TestCheckpointStatePersistence:
    """Tests for checkpoint state persistence during execution."""

    def test_checkpoint_state_persistence(self):
        """Test that checkpoint state persists across multiple calls."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Create initial checkpoint
        with patch("time.time", return_value=1000.0):
            log_checkpoint("persistence_test")

        # Verify initial state
        stats = functional._checkpoint_stats["persistence_test"]
        assert stats["last_checkpoint"] == 1000.0
        assert len(stats["times"]) == 0

        # Add more checkpoints
        with patch("time.time", return_value=1003.0):
            log_checkpoint("persistence_test")

        with patch("time.time", return_value=1007.0):
            log_checkpoint("persistence_test")

        # Verify accumulated state
        stats = functional._checkpoint_stats["persistence_test"]
        assert stats["last_checkpoint"] == 1007.0
        assert len(stats["times"]) == 2
        assert stats["times"] == [3.0, 4.0]

    def test_multiple_concurrent_checkpoints(self):
        """Test multiple checkpoint IDs running concurrently."""
        setup_log_file_and_logger(setup_independent_logging=True)

        checkpoint_times = {
            "process_a": [1000.0, 1002.0, 1005.0],
            "process_b": [1001.0, 1004.0, 1008.0],
            "process_c": [1000.5, 1003.5, 1007.5],
        }

        # Interleave checkpoint calls
        for i in range(3):
            for process_id, times in checkpoint_times.items():
                with patch("time.time", return_value=times[i]):
                    log_checkpoint(process_id)

        # Verify each process maintained separate state
        assert len(functional._checkpoint_stats) == 3

        # Check timing calculations
        stats_a = functional._checkpoint_stats["process_a"]
        stats_b = functional._checkpoint_stats["process_b"]
        stats_c = functional._checkpoint_stats["process_c"]

        assert stats_a["times"] == [2.0, 3.0]  # 1002-1000, 1005-1002
        assert stats_b["times"] == [3.0, 4.0]  # 1004-1001, 1008-1004
        assert stats_c["times"] == [3.0, 4.0]  # 1003.5-1000.5, 1007.5-1003.5
