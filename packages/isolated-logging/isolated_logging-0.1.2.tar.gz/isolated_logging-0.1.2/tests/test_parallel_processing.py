"""
Comprehensive test suite for parallel processing functionality.

This module tests the log_timed_parallel_loop function including parallel execution,
error handling, timing measurements, and behavior with and without loky dependency.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

import isolated_logging.functional as functional
from isolated_logging import log_timed_parallel_loop, setup_log_file_and_logger


class TestLogTimedParallelLoopBasicFunctionality:
    """Tests for basic parallel loop functionality with loky available."""

    @pytest.mark.parallel
    def test_parallel_processing_with_loky(self, monkeypatch):
        """Test parallel processing when loky is available."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Mock loky components
        mock_executor = MagicMock()
        mock_future1 = MagicMock()
        mock_future2 = MagicMock()

        # Mock results
        mock_future1.result.return_value = ("result1", 0.5, "item1")
        mock_future2.result.return_value = ("result2", 0.7, "item2")

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.side_effect = [mock_future1, mock_future2]

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[mock_future1, mock_future2])

        # Patch loky functions
        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            return x * 2

        results, errors = log_timed_parallel_loop(["item1", "item2"], test_func, {}, n_jobs=2)

        assert results == ["result1", "result2"]
        assert errors == []
        assert mock_executor.submit.call_count == 2

    def test_parallel_loop_without_loky_raises_error(self, monkeypatch):
        """Test that missing loky raises ImportError."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Mock loky as unavailable
        monkeypatch.setattr(functional, "as_completed", None)
        monkeypatch.setattr(functional, "get_reusable_executor", None)

        def test_func(x):
            return x * 2

        with pytest.raises(ImportError, match="loky is required for parallel processing"):
            log_timed_parallel_loop([1, 2], test_func, {})

    @pytest.mark.parallel
    def test_function_with_kwargs(self, monkeypatch):
        """Test parallel processing with function kwargs."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Setup mock executor
        mock_executor = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = ("result", 0.5, "item")

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.return_value = mock_future

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[mock_future])

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x, multiplier=2):
            return x * multiplier

        results, errors = log_timed_parallel_loop([5], test_func, {"multiplier": 3}, n_jobs=1)

        # Verify the function was called with kwargs
        mock_executor.submit.assert_called_once()
        args, kwargs = mock_executor.submit.call_args
        assert args[0] == functional.timed_func  # The wrapper function
        assert args[1] == test_func  # The user function
        assert args[2] == 5  # The item
        assert kwargs == {"multiplier": 3}  # The function kwargs


class TestErrorHandlingInParallelProcessing:
    """Tests for error handling in parallel processing."""

    @pytest.mark.parallel
    def test_exception_handling_continue_on_error(self, monkeypatch):
        """Test that exceptions are collected when raise_exceptions=False."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Setup mock executor with one success and one failure
        mock_executor = MagicMock()
        mock_future_success = MagicMock()
        mock_future_error = MagicMock()

        mock_future_success.result.return_value = ("success", 0.5, "item1")
        mock_future_error.result.side_effect = ValueError("Test error")

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.side_effect = [mock_future_success, mock_future_error]

        # Mock futures mapping
        mock_as_completed = Mock(return_value=[mock_future_success, mock_future_error])
        mock_get_executor = Mock(return_value=mock_executor)

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            if x == "item2":
                raise ValueError("Test error")
            return x

        # Patch the futures dict creation
        with patch.object(mock_executor, "submit") as mock_submit:
            mock_submit.side_effect = [mock_future_success, mock_future_error]

            results, errors = log_timed_parallel_loop(
                ["item1", "item2"], test_func, {}, raise_exceptions=False
            )

        assert results == ["success"]
        assert len(errors) == 1
        assert "error" in errors[0]
        assert errors[0]["item"] == "item2"

    @pytest.mark.parallel
    def test_exception_handling_raise_on_error(self, monkeypatch):
        """Test that exceptions are raised when raise_exceptions=True."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Setup mock executor that raises an exception
        mock_executor = MagicMock()
        mock_future = MagicMock()
        mock_future.result.side_effect = ValueError("Test error")

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.return_value = mock_future
        mock_executor.shutdown = Mock()

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[mock_future])

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            log_timed_parallel_loop(["item1"], test_func, {}, raise_exceptions=True)

        # Verify executor shutdown was called
        mock_executor.shutdown.assert_called_once_with(wait=False)

    @pytest.mark.parallel
    def test_keyboard_interrupt_handling(self, monkeypatch):
        """Test that KeyboardInterrupt is always raised regardless of raise_exceptions."""
        setup_log_file_and_logger(setup_independent_logging=True)

        mock_executor = MagicMock()
        mock_future = MagicMock()
        mock_future.result.side_effect = KeyboardInterrupt("User interrupted")

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.return_value = mock_future

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[mock_future])

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            return x

        with pytest.raises(KeyboardInterrupt):
            log_timed_parallel_loop(
                ["item1"],
                test_func,
                {},
                raise_exceptions=False,  # Should still raise KeyboardInterrupt
            )


class TestTimingAndStatistics:
    """Tests for timing measurements and statistics in parallel processing."""

    @pytest.mark.parallel
    def test_timing_statistics_collection(self, monkeypatch):
        """Test that timing statistics are collected correctly."""
        setup_log_file_and_logger(setup_independent_logging=True)

        mock_executor = MagicMock()
        mock_future1 = MagicMock()
        mock_future2 = MagicMock()

        # Different timing for each task
        mock_future1.result.return_value = ("result1", 0.5, "item1")
        mock_future2.result.return_value = ("result2", 1.5, "item2")

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.side_effect = [mock_future1, mock_future2]

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[mock_future1, mock_future2])

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            return x

        results, errors = log_timed_parallel_loop(["item1", "item2"], test_func, {})

        log_content = functional.read_log()

        # Should log completion with timing
        assert "Finished processing" in log_content
        assert "item1" in log_content
        assert "0.50 seconds" in log_content
        assert "item2" in log_content
        assert "1.50 seconds" in log_content

        # Should log final statistics
        assert "Average time per iteration:" in log_content
        assert "iterations per second" in log_content

    @patch("time.time")
    @pytest.mark.parallel
    def test_eta_calculation(self, mock_time, monkeypatch):
        """Test ETA calculation in parallel processing."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_time.side_effect = [1000.0, 1001.0, 1002.0]  # Mock progression

        mock_executor = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = ("result", 1.0, "item1")

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.return_value = mock_future

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[mock_future])

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            return x

        # Use list with known length for ETA calculation
        results, errors = log_timed_parallel_loop(
            ["item1", "item2", "item3"],  # 3 items
            test_func,
            {},
        )

        log_content = functional.read_log()
        # Should contain ETA information
        assert "Estimated time remaining:" in log_content
        assert "items remaining" in log_content

    @pytest.mark.parallel
    def test_instant_iteration_filtering(self, monkeypatch):
        """Test instant iteration filtering in parallel processing."""
        setup_log_file_and_logger(setup_independent_logging=True)

        mock_executor = MagicMock()
        mock_future_fast = MagicMock()
        mock_future_slow = MagicMock()

        # One very fast, one slower
        mock_future_fast.result.return_value = ("fast_result", 0.0001, "item1")  # Below threshold
        mock_future_slow.result.return_value = ("slow_result", 0.1, "item2")  # Above threshold

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.side_effect = [mock_future_fast, mock_future_slow]

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[mock_future_fast, mock_future_slow])

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            return x

        results, errors = log_timed_parallel_loop(
            ["item1", "item2"], test_func, {}, ignore_instant_iterations=True, threshold=0.001
        )

        # Should have both results but only slow one contributes to statistics
        assert results == ["slow_result"]  # Fast one filtered out
        assert errors == []

        log_content = functional.read_log()
        # Should see completion log only for slow item
        assert "Finished processing" in log_content
        assert "item2" in log_content


class TestParallelProcessingParameters:
    """Tests for various parameter configurations."""

    @pytest.mark.parallel
    def test_different_worker_counts(self, monkeypatch):
        """Test parallel processing with different worker counts."""
        setup_log_file_and_logger(setup_independent_logging=True)

        for n_jobs in [1, 2, 4]:
            mock_executor = MagicMock()
            mock_future = MagicMock()
            mock_future.result.return_value = ("result", 0.5, "item")

            mock_executor.__enter__.return_value = mock_executor
            mock_executor.__exit__.return_value = None
            mock_executor.submit.return_value = mock_future

            mock_get_executor = Mock(return_value=mock_executor)
            mock_as_completed = Mock(return_value=[mock_future])

            monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
            monkeypatch.setattr(functional, "as_completed", mock_as_completed)

            def test_func(x):
                return x

            results, errors = log_timed_parallel_loop(["item"], test_func, {}, n_jobs=n_jobs)

            # Verify executor was called with correct max_workers
            mock_get_executor.assert_called_with(max_workers=n_jobs)

    @pytest.mark.parallel
    def test_custom_loop_name(self, monkeypatch):
        """Test parallel processing with custom loop name."""
        setup_log_file_and_logger(setup_independent_logging=True)

        mock_executor = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = ("result", 0.5, "item")

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.return_value = mock_future

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[mock_future])

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            return x

        results, errors = log_timed_parallel_loop(
            ["item"], test_func, {}, loop_name="CustomParallelLoop"
        )

        log_content = functional.read_log()
        assert "(CustomParallelLoop)" in log_content

    @pytest.mark.parallel
    def test_custom_threshold(self, monkeypatch):
        """Test parallel processing with custom threshold."""
        setup_log_file_and_logger(setup_independent_logging=True)

        mock_executor = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = ("result", 0.05, "item")  # 0.05 seconds

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.return_value = mock_future

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[mock_future])

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            return x

        # With threshold 0.1, the 0.05 second task should be filtered
        results, errors = log_timed_parallel_loop(
            ["item"], test_func, {}, threshold=0.1, ignore_instant_iterations=True
        )

        assert results == []  # Filtered out
        assert errors == []


class TestTimedFunctionWrapper:
    """Tests for the timed_func wrapper function."""

    def test_timed_func_basic_functionality(self):
        """Test that timed_func properly wraps and times function execution."""

        def test_function(x, multiplier=2):
            return x * multiplier

        result, elapsed_time, original_item = functional.timed_func(test_function, 5, multiplier=3)

        assert result == 15  # 5 * 3
        assert isinstance(elapsed_time, float)
        assert elapsed_time >= 0
        assert original_item == 5

    def test_timed_func_with_exception(self):
        """Test timed_func behavior when wrapped function raises exception."""

        def error_function(x):
            raise ValueError(f"Error with {x}")

        with pytest.raises(ValueError, match="Error with 5"):
            functional.timed_func(error_function, 5)

    @patch("time.time")
    def test_timed_func_timing_accuracy(self, mock_time):
        """Test that timed_func accurately measures execution time."""
        mock_time.side_effect = [1000.0, 1002.5]  # 2.5 second execution

        def slow_function(x):
            return x * 2

        result, elapsed_time, item = functional.timed_func(slow_function, 5)

        assert result == 10
        assert elapsed_time == 2.5
        assert item == 5

    def test_timed_func_with_complex_args(self):
        """Test timed_func with complex arguments and keyword arguments."""

        def complex_function(data, processor=None, **kwargs):
            result = sum(data)
            if processor:
                result = processor(result)
            return result + kwargs.get("offset", 0)

        def double(x):
            return x * 2

        result, elapsed_time, original_data = functional.timed_func(
            complex_function, [1, 2, 3], processor=double, offset=10
        )

        # sum([1,2,3]) = 6, doubled = 12, + 10 = 22
        assert result == 22
        assert original_data == [1, 2, 3]


class TestLoggingIntegration:
    """Tests for logging integration in parallel processing."""

    @pytest.mark.parallel
    def test_completion_logging(self, monkeypatch):
        """Test that task completion is logged."""
        setup_log_file_and_logger(setup_independent_logging=True)

        mock_executor = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = ("result", 0.5, "test_item")

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.return_value = mock_future

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[mock_future])

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            return x

        results, errors = log_timed_parallel_loop(["test_item"], test_func, {})

        log_content = functional.read_log()
        assert "Finished processing" in log_content
        assert "test_item" in log_content
        assert "0.50 seconds" in log_content

    @pytest.mark.parallel
    def test_error_logging(self, monkeypatch):
        """Test that errors are logged properly."""
        setup_log_file_and_logger(setup_independent_logging=True)

        mock_executor = MagicMock()
        mock_future = MagicMock()
        mock_future.result.side_effect = RuntimeError("Test runtime error")

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.return_value = mock_future

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[mock_future])

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            return x

        results, errors = log_timed_parallel_loop(
            ["error_item"], test_func, {}, raise_exceptions=False
        )

        log_content = functional.read_log()
        assert "Exception for error_item: Test runtime error" in log_content

    @pytest.mark.parallel
    def test_external_logger_integration(self, mock_logger, monkeypatch):
        """Test integration with external logger in parallel processing."""
        setup_log_file_and_logger(logger=mock_logger)

        mock_executor = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = ("result", 0.5, "item")

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.return_value = mock_future

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[mock_future])

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            return x

        results, errors = log_timed_parallel_loop(["item"], test_func, {})

        # Verify external logger was called
        assert mock_logger.info.call_count > 0


class TestEdgeCasesAndBoundaryConditions:
    """Tests for edge cases in parallel processing."""

    @pytest.mark.parallel
    def test_empty_iterable(self, monkeypatch):
        """Test parallel processing with empty iterable."""
        setup_log_file_and_logger(setup_independent_logging=True)

        mock_executor = MagicMock()
        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.return_value = None

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[])

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            return x

        results, errors = log_timed_parallel_loop([], test_func, {})

        assert results == []
        assert errors == []

    @pytest.mark.parallel
    def test_single_item_processing(self, monkeypatch):
        """Test parallel processing with single item."""
        setup_log_file_and_logger(setup_independent_logging=True)

        mock_executor = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = ("single_result", 0.5, "single_item")

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.return_value = mock_future

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[mock_future])

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            return x

        results, errors = log_timed_parallel_loop(["single_item"], test_func, {})

        assert results == ["single_result"]
        assert errors == []

    @pytest.mark.parallel
    def test_all_items_filtered_by_threshold(self, monkeypatch):
        """Test when all items are filtered by instant iteration threshold."""
        setup_log_file_and_logger(setup_independent_logging=True)

        mock_executor = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = ("result", 0.0001, "item")  # Very fast

        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = None
        mock_executor.submit.return_value = mock_future

        mock_get_executor = Mock(return_value=mock_executor)
        mock_as_completed = Mock(return_value=[mock_future])

        monkeypatch.setattr(functional, "get_reusable_executor", mock_get_executor)
        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        def test_func(x):
            return x

        results, errors = log_timed_parallel_loop(
            ["item"], test_func, {}, ignore_instant_iterations=True, threshold=0.001
        )

        assert results == []  # All filtered out
        assert errors == []

        log_content = functional.read_log()
        # Should still show completion statistics even with no recorded items
        assert "Average time per iteration: 0.00 seconds" in log_content
