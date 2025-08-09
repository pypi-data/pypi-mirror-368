"""
Comprehensive test suite for the log_timed_loop context manager.

This module tests the context manager functionality including iteration timing,
ETA calculations, statistics tracking, and integration with the logging system.
"""

import time
from unittest.mock import patch

import pytest

import isolated_logging.functional as functional
from isolated_logging import log_timed_loop, setup_log_file_and_logger


class TestLogTimedLoopBasicFunctionality:
    """Tests for basic log_timed_loop functionality."""

    def test_basic_iteration_over_list(self, sample_iterable):
        """Test basic iteration functionality with a list."""
        setup_log_file_and_logger(setup_independent_logging=True)

        items = []
        for item in log_timed_loop(sample_iterable):
            items.append(item)

        assert items == sample_iterable
        assert len(items) == 5

    def test_iteration_over_range(self):
        """Test iteration over range objects."""
        setup_log_file_and_logger(setup_independent_logging=True)

        items = []
        for item in log_timed_loop(range(3)):
            items.append(item)

        assert items == [0, 1, 2]

    def test_iteration_over_generator(self):
        """Test iteration over generator objects."""
        setup_log_file_and_logger(setup_independent_logging=True)

        def test_generator():
            yield "a"
            yield "b"
            yield "c"

        items = []
        for item in log_timed_loop(test_generator()):
            items.append(item)

        assert items == ["a", "b", "c"]

    def test_empty_iterable(self):
        """Test iteration over empty iterable."""
        setup_log_file_and_logger(setup_independent_logging=True)

        items = []
        for item in log_timed_loop([]):
            items.append(item)

        assert items == []
        # Should not crash or log errors

    def test_single_item_iterable(self):
        """Test iteration over single-item iterable."""
        setup_log_file_and_logger(setup_independent_logging=True)

        items = []
        for item in log_timed_loop(["single"]):
            items.append(item)

        assert items == ["single"]


class TestLoopStatisticsTracking:
    """Tests for loop statistics tracking and calculations."""

    @patch("time.time")
    def test_statistics_collection(self, mock_time, sample_iterable):
        """Test that loop statistics are collected correctly."""
        setup_log_file_and_logger(setup_independent_logging=True)
        # Mock timing: 1000, 1001, 1002, 1003, etc.
        mock_time.side_effect = [1000 + i * 0.5 for i in range(20)]

        items = []
        for item in log_timed_loop(sample_iterable):
            items.append(item)
            # Simulate some processing time
            time.sleep(0.01)

        # Check that statistics were recorded
        assert len(functional._loop_stats) > 0

        # Get the loop stats (using id of the iterable)
        loop_id = id(sample_iterable)
        loop_stats = functional._loop_stats[loop_id]

        assert "times" in loop_stats
        assert "iterations" in loop_stats
        assert loop_stats["iterations"] == 5

    def test_statistics_with_custom_loop_id(self):
        """Test statistics tracking with custom loop ID."""
        setup_log_file_and_logger(setup_independent_logging=True)
        custom_id = "my_custom_loop"

        for _ in log_timed_loop([1, 2, 3], loop_id=custom_id):
            time.sleep(0.01)

        assert custom_id in functional._loop_stats
        assert functional._loop_stats[custom_id]["iterations"] == 3

    def test_statistics_isolation_between_loops(self):
        """Test that statistics are isolated between different loops."""
        setup_log_file_and_logger(setup_independent_logging=True)

        list1 = [1, 2]
        list2 = [3, 4, 5]

        for _ in log_timed_loop(list1, loop_id="loop1"):
            time.sleep(0.01)

        for _ in log_timed_loop(list2, loop_id="loop2"):
            time.sleep(0.01)

        assert functional._loop_stats["loop1"]["iterations"] == 2
        assert functional._loop_stats["loop2"]["iterations"] == 3

    @patch("numpy.mean")
    def test_average_calculation(self, mock_mean, sample_iterable):
        """Test that average iteration time is calculated correctly."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_mean.return_value = 1.5

        for _ in log_timed_loop(sample_iterable):
            time.sleep(0.01)

        # Verify numpy.mean was called
        mock_mean.assert_called()


class TestInstantIterationFiltering:
    """Tests for instant iteration filtering functionality."""

    @patch("time.time")
    def test_ignore_instant_iterations_filters_fast(self, mock_time):
        """Test that instant iterations are filtered when enabled."""
        setup_log_file_and_logger(setup_independent_logging=True)
        # Make some iterations very fast (below threshold)
        mock_time.side_effect = [
            1000.0,  # Start time
            1000.0,
            1000.0001,  # Iteration 1: very fast
            1000.0001,
            1000.1,  # Iteration 2: slow
            1000.1,
            1000.1001,  # Iteration 3: very fast
        ]

        for _ in log_timed_loop([1, 2, 3], ignore_instant_iterations=True, threshold=0.001):
            pass

        # Only iteration 2 should be tracked
        loop_stats = list(functional._loop_stats.values())[0]
        assert loop_stats["iterations"] == 1  # Only one non-instant iteration

    @patch("time.time")
    def test_ignore_instant_iterations_false_tracks_all(self, mock_time):
        """Test that all iterations are tracked when filtering is disabled."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_time.side_effect = [
            1000.0,  # Start time
            1000.0,
            1000.0001,  # Very fast iteration 1
            1000.0001,
            1000.0002,  # Very fast iteration 2
        ]

        for _ in log_timed_loop([1, 2], ignore_instant_iterations=False):
            pass

        loop_stats = list(functional._loop_stats.values())[0]
        assert loop_stats["iterations"] == 2  # Both iterations tracked

    def test_custom_threshold(self):
        """Test custom threshold for instant iteration filtering."""
        setup_log_file_and_logger(setup_independent_logging=True)

        with patch("time.time", side_effect=[1000.0, 1000.0, 1000.05, 1000.05, 1000.1]):
            # 0.05 second iteration with 0.1 threshold
            for _ in log_timed_loop([1], ignore_instant_iterations=True, threshold=0.1):
                pass

        # Should be filtered with 0.1 threshold
        loop_stats = list(functional._loop_stats.values())[0]
        assert loop_stats["iterations"] == 0


class TestETACalculations:
    """Tests for ETA (Estimated Time of Arrival) calculations."""

    @patch("time.time")
    def test_eta_calculation_with_known_length(self, mock_time):
        """Test ETA calculation for iterables with known length."""
        setup_log_file_and_logger(setup_independent_logging=True)
        # Setup timing: start at 1000, each iteration takes 1 second
        mock_time.side_effect = [
            1000.0,  # Start time
            1000.0,
            1001.0,  # Iteration 1: 1 second
            1001.0,
            1002.0,  # Iteration 2: 1 second
            1002.0,
            1003.0,  # Iteration 3: 1 second
        ]

        items = [1, 2, 3]  # Known length = 3
        for _, _ in enumerate(log_timed_loop(items)):
            pass

        log_content = functional.read_log()
        # Should contain ETA information
        assert "Estimated time remaining:" in log_content
        assert "iterations remaining" in log_content

    def test_eta_without_known_length(self):
        """Test behavior when iterable has no known length."""
        setup_log_file_and_logger(setup_independent_logging=True)

        def generator():
            yield 1
            yield 2
            yield 3

        for _ in log_timed_loop(generator()):
            time.sleep(0.01)
        # Should not contain ETA information for generators
        # (they don't have __len__)
        # This tests the hasattr(iterable, "__len__") condition

    @patch("time.time")
    def test_eta_accuracy(self, mock_time):
        """Test ETA calculation accuracy."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_time.side_effect = [
            1000.0,  # Start
            1000.0,
            1001.0,  # Item 1: 1 sec
            1001.0,
            1002.0,  # Item 2: 1 sec
            1002.0,
            1003.0,  # Item 3: 1 sec (for partial processing)
        ]

        items = [1, 2, 3, 4, 5]  # 5 items total, 3 remaining after 2
        processed_items = []

        for i, item in enumerate(log_timed_loop(items)):
            processed_items.append(item)
            if i == 1:  # After processing 2 items (0-indexed)
                break

        log_content = functional.read_log()
        # After 1 item at 1 sec each, ETA for 4 remaining should be ~4 seconds
        assert "4.00 seconds" in log_content


class TestLoopNamingAndIdentification:
    """Tests for loop naming and identification features."""

    def test_loop_with_custom_name(self):
        """Test loop with custom name appears in logs."""
        setup_log_file_and_logger(setup_independent_logging=True)

        for _ in log_timed_loop([1, 2], loop_name="MyCustomLoop"):
            time.sleep(0.01)

        log_content = functional.read_log()
        assert "(MyCustomLoop)" in log_content

    def test_loop_without_name(self):
        """Test loop without custom name works correctly."""
        setup_log_file_and_logger(setup_independent_logging=True)

        for _ in log_timed_loop([1, 2]):
            time.sleep(0.01)

        log_content = functional.read_log()
        # Should not contain custom name parentheses
        assert "Iteration 1:" in log_content
        assert "Iteration 2:" in log_content

    def test_loop_id_vs_loop_name(self):
        """Test difference between loop_id and loop_name parameters."""
        setup_log_file_and_logger(setup_independent_logging=True)

        for _ in log_timed_loop([1, 2], loop_id="custom_id", loop_name="CustomName"):
            time.sleep(0.01)

        # Name should appear in logs
        log_content = functional.read_log()
        assert "(CustomName)" in log_content

        # ID should be used for statistics
        assert "custom_id" in functional._loop_stats


class TestYieldStatisticsFeature:
    """Tests for the yield_statistics feature."""

    def test_yield_statistics_enabled(self):
        """Test yield_statistics=True returns statistics with each item."""
        setup_log_file_and_logger(setup_independent_logging=True)

        items_and_stats = []
        for item_data in log_timed_loop([1, 2], yield_statistics=True):
            items_and_stats.append(item_data)

        # Should yield tuples of (item, statistics)
        assert len(items_and_stats) == 2
        item1, stats1 = items_and_stats[0]
        item2, stats2 = items_and_stats[1]

        assert item1 == 1
        assert item2 == 2
        assert isinstance(stats1, dict)
        assert isinstance(stats2, dict)

        # Check statistics structure
        expected_keys = [
            "loop_id",
            "loop_name",
            "total_items",
            "start_time",
            "instant_items",
            "completed_items",
            "current_iteration",
            "total_elapsed_time",
            "average_time_per_item",
            "remaining_items",
            "eta",
        ]
        for key in expected_keys:
            assert key in stats1

    def test_yield_statistics_disabled(self):
        """Test yield_statistics=False returns only items."""
        setup_log_file_and_logger(setup_independent_logging=True)

        items = []
        for item in log_timed_loop([1, 2], yield_statistics=False):
            items.append(item)

        # Should yield only items, not tuples
        assert items == [1, 2]
        assert all(not isinstance(item, tuple) for item in items)

    def test_statistics_content_accuracy(self):
        """Test that yielded statistics contain accurate information."""
        setup_log_file_and_logger(setup_independent_logging=True)

        test_items = [1, 2, 3]
        for i, (_, stats) in enumerate(
            log_timed_loop(test_items, yield_statistics=True, loop_name="TestLoop")
        ):
            assert stats["current_iteration"] == i
            assert stats["loop_name"] == "TestLoop"
            assert stats["total_items"] == 3

            if i == 1:  # Second iteration
                assert stats["completed_items"] >= 0  # At least some items completed
                assert stats["remaining_items"] <= 3  # Some items remaining


class TestLoggingIntegration:
    """Tests for integration with the logging system."""

    def test_iteration_start_logs(self):
        """Test that iteration start is logged."""
        setup_log_file_and_logger(setup_independent_logging=True)

        for _ in log_timed_loop([1, 2]):
            time.sleep(0.01)

        log_content = functional.read_log()
        assert "Iteration 1: Started processing" in log_content
        assert "Iteration 2: Started processing" in log_content

    def test_iteration_completion_logs(self):
        """Test that iteration completion is logged with timing."""
        setup_log_file_and_logger(setup_independent_logging=True)

        for _ in log_timed_loop([1, 2]):
            time.sleep(0.01)

        log_content = functional.read_log()
        assert "Iteration 1: Finished processing" in log_content
        assert "Iteration 2: Finished processing" in log_content
        assert "seconds" in log_content

    def test_loop_summary_logs(self):
        """Test that loop summary statistics are logged."""
        setup_log_file_and_logger(setup_independent_logging=True)

        for _ in log_timed_loop([1, 2, 3]):
            time.sleep(0.01)

        log_content = functional.read_log()
        assert "Average time per iteration:" in log_content
        assert "iterations per second" in log_content
        assert "Total iterations:" in log_content

    def test_external_logger_integration(self, mock_logger):
        """Test integration with external logger."""
        setup_log_file_and_logger(logger=mock_logger)

        for _ in log_timed_loop([1, 2]):
            time.sleep(0.01)

        # Verify external logger was called
        assert mock_logger.info.call_count > 0

    def test_no_logging_setup_warning(self, captured_output):
        """Test behavior when no logging is set up."""
        # Don't call setup_log_file_and_logger

        for _ in log_timed_loop([1]):
            pass

        # Should show warning
        assert any("No log file or logger set up!" in line for line in captured_output)


class TestEdgeCasesAndErrorHandling:
    """Tests for edge cases and error conditions."""

    def test_very_large_iterable(self):
        """Test with very large iterable."""
        setup_log_file_and_logger(setup_independent_logging=True)

        large_range = range(1000)
        count = 0

        # Only process first 10 items to avoid long test
        for _ in log_timed_loop(large_range):
            count += 1
            if count >= 10:
                break

        assert count == 10
        # Should handle large iterables without issues

    def test_iterable_with_complex_objects(self):
        """Test with iterable containing complex objects."""
        setup_log_file_and_logger(setup_independent_logging=True)

        complex_items = [
            {"name": "item1", "data": [1, 2, 3]},
            {"name": "item2", "data": [4, 5, 6]},
        ]

        processed = []
        for item in log_timed_loop(complex_items):
            processed.append(item["name"])

        assert processed == ["item1", "item2"]

    def test_nested_loops(self):
        """Test nested log_timed_loop usage."""
        setup_log_file_and_logger(setup_independent_logging=True)

        outer_items = [1, 2]
        inner_items = ["a", "b"]

        results = []
        for outer in log_timed_loop(outer_items, loop_name="Outer"):
            for inner in log_timed_loop(inner_items, loop_name="Inner"):
                results.append(f"{outer}{inner}")

        assert results == ["1a", "1b", "2a", "2b"]

        # Should track both loops separately
        assert len(functional._loop_stats) == 2

    def test_break_in_loop(self):
        """Test breaking out of loop early."""
        setup_log_file_and_logger(setup_independent_logging=True)

        items_processed = []
        for item in log_timed_loop([1, 2, 3, 4, 5]):
            items_processed.append(item)
            if item == 3:
                break

        assert items_processed == [1, 2, 3]
        # Statistics should reflect only processed items

    def test_continue_in_loop(self):
        """Test continue statement in loop."""
        setup_log_file_and_logger(setup_independent_logging=True)

        even_items = []
        for item in log_timed_loop([1, 2, 3, 4, 5]):
            if item % 2 == 1:
                continue
            even_items.append(item)

        assert even_items == [2, 4]
        # All iterations should still be logged

    def test_exception_during_iteration(self):
        """Test that exceptions during iteration are handled properly."""
        setup_log_file_and_logger(setup_independent_logging=True)

        def problematic_processing(item):
            if item == 3:
                raise ValueError("Test error")
            return item

        processed = []
        with pytest.raises(ValueError):
            for item in log_timed_loop([1, 2, 3, 4]):
                processed.append(problematic_processing(item))

        # Should have processed items before error
        assert processed == [1, 2]
