"""
Comprehensive test suite for the log_timed_function decorator.

This module tests the decorator functionality including timing, statistics tracking,
instant execution filtering, and integration with the logging system.
"""

import time
from unittest.mock import patch

import pytest

import isolated_logging.functional as functional
from isolated_logging import log_timed_function, setup_log_file_and_logger


class TestLogTimedFunctionDecorator:
    """Tests for the log_timed_function decorator basic functionality."""

    def test_decorator_preserves_function_behavior(self, sample_function):
        """Test that decorator preserves original function behavior."""
        setup_log_file_and_logger(setup_independent_logging=True)

        decorated_func = log_timed_function(ignore_instant_returns=False)(sample_function)
        result = decorated_func(5, y=3)

        assert result == 8  # 5 + 3
        assert decorated_func.__name__ == sample_function.__name__

    def test_decorator_preserves_function_signature(self, sample_function):
        """Test that decorator preserves function signature and metadata."""
        decorated_func = log_timed_function(ignore_instant_returns=False)(sample_function)

        assert decorated_func.__name__ == sample_function.__name__
        assert decorated_func.__doc__ == sample_function.__doc__

    def test_decorator_with_args_and_kwargs(self):
        """Test decorator handles functions with various argument patterns."""
        setup_log_file_and_logger(setup_independent_logging=True)

        @log_timed_function(ignore_instant_returns=False)
        def test_func(a, b, c=10, *args, **kwargs):
            return a + b + c + sum(args) + sum(kwargs.values())

        result = test_func(1, 2, 3, 4, 5, x=6, y=7)
        expected = 1 + 2 + 3 + 4 + 5 + 6 + 7  # 28

        assert result == expected

    def test_decorator_with_no_args_function(self):
        """Test decorator with function that takes no arguments."""
        setup_log_file_and_logger(setup_independent_logging=True)

        @log_timed_function(ignore_instant_returns=False)
        def no_args_func():
            return 42

        result = no_args_func()
        assert result == 42

    def test_decorator_with_exception_function(self, exception_function):
        """Test that decorator properly handles exceptions from decorated functions."""
        setup_log_file_and_logger(setup_independent_logging=True)

        decorated_func = log_timed_function(ignore_instant_returns=False)(exception_function)

        with pytest.raises(ValueError, match="Test error with value: 5"):
            decorated_func(5, error_type="value")

        # Should still track the function call in stats even with exception
        assert "error_function" in functional._function_stats


class TestTimingAndStatistics:
    """Tests for timing measurements and statistics tracking."""

    @patch("time.time")
    def test_timing_measurement(self, mock_time, sample_function):
        """Test that decorator accurately measures execution time."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_time.side_effect = [1000.0, 1001.5]  # 1.5 second execution

        decorated_func = log_timed_function(ignore_instant_returns=False)(sample_function)
        decorated_func(5)

        # Check that timing was recorded
        assert "test_function" in functional._function_stats
        assert len(functional._function_stats["test_function"]) == 1
        assert functional._function_stats["test_function"][0] == 1.5

    def test_statistics_accumulation(self, fast_function):
        """Test that statistics accumulate over multiple function calls."""
        setup_log_file_and_logger(setup_independent_logging=True)

        decorated_func = log_timed_function(ignore_instant_returns=False)(fast_function)

        # Make multiple calls
        for i in range(5):
            decorated_func(i)

        # Check statistics
        stats = functional._function_stats["fast_test_function"]
        assert len(stats) == 5
        assert all(isinstance(t, float) for t in stats)

    @patch("numpy.mean")
    @patch("numpy.std")
    def test_statistics_calculation(self, mock_std, mock_mean, sample_function):
        """Test that decorator calculates and logs correct statistics."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_mean.return_value = 1.5
        mock_std.return_value = 0.3

        decorated_func = log_timed_function(ignore_instant_returns=False)(sample_function)
        decorated_func(5)
        decorated_func(10)  # Call twice to trigger std calculation

        # Verify numpy functions were called
        mock_mean.assert_called()
        mock_std.assert_called()

    def test_statistics_with_single_call(self, sample_function):
        """Test statistics calculation with only one function call."""
        setup_log_file_and_logger(setup_independent_logging=True)

        decorated_func = log_timed_function(ignore_instant_returns=False)(sample_function)
        decorated_func(5)

        # Should handle single call case (std dev = 0)
        stats = functional._function_stats["test_function"]
        assert len(stats) == 1

    def test_statistics_isolation_between_functions(self):
        """Test that statistics are isolated between different functions."""
        setup_log_file_and_logger(setup_independent_logging=True)

        @log_timed_function(ignore_instant_returns=False)
        def func1():
            return 1

        @log_timed_function(ignore_instant_returns=False)
        def func2():
            return 2

        func1()
        func1()
        func2()

        assert len(functional._function_stats["func1"]) == 2
        assert len(functional._function_stats["func2"]) == 1


class TestInstantExecutionFiltering:
    """Tests for instant execution filtering functionality."""

    @patch("time.time")
    def test_ignore_instant_returns_filters_fast_calls(self, mock_time, fast_function):
        """Test that instant returns are filtered when ignore_instant_returns=True."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_time.side_effect = [1000.0, 1000.0005]  # 0.0005 second (below threshold)

        decorated_func = log_timed_function(ignore_instant_returns=True)(fast_function)
        result = decorated_func(5)

        assert result == 10  # Function still executes
        assert "fast_test_function" not in functional._function_stats  # But not tracked

    @patch("time.time")
    def test_ignore_instant_returns_tracks_slow_calls(self, mock_time, slow_function):
        """Test that slow calls are tracked even with ignore_instant_returns=True."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_time.side_effect = [1000.0, 1000.5]  # 0.5 second (above threshold)

        decorated_func = log_timed_function(ignore_instant_returns=True)(slow_function)
        decorated_func(5)

        assert "slow_test_function" in functional._function_stats
        assert len(functional._function_stats["slow_test_function"]) == 1

    @patch("time.time")
    def test_custom_threshold(self, mock_time, sample_function):
        """Test decorator with custom threshold value."""
        setup_log_file_and_logger(setup_independent_logging=True)
        mock_time.side_effect = [1000.0, 1000.05]  # 0.05 second

        # Use higher threshold - should filter this call
        decorated_func = log_timed_function(ignore_instant_returns=True, threshold=0.1)(
            sample_function
        )
        decorated_func(5)

        assert "test_function" not in functional._function_stats

    @patch("time.time")
    def test_threshold_boundary_conditions(self, mock_time, sample_function):
        """Test behavior at threshold boundaries."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Exactly at threshold
        mock_time.side_effect = [1000.0, 1000.001]  # Exactly 0.001 second
        decorated_func = log_timed_function(ignore_instant_returns=True, threshold=0.001)(
            sample_function
        )
        decorated_func(5)

        # Should be filtered (< threshold, not <=)
        assert "test_function" not in functional._function_stats

    def test_ignore_instant_returns_false_always_tracks(self, fast_function):
        """Test that ignore_instant_returns=False always tracks calls."""
        setup_log_file_and_logger(setup_independent_logging=True)

        decorated_func = log_timed_function(ignore_instant_returns=False)(fast_function)

        # Make multiple fast calls
        for i in range(3):
            decorated_func(i)

        # All should be tracked
        assert len(functional._function_stats["fast_test_function"]) == 3


class TestLoggingIntegration:
    """Tests for integration with the logging system."""

    def test_logs_function_start(self, sample_function):
        """Test that decorator logs function start with arguments."""
        setup_log_file_and_logger(setup_independent_logging=True)

        decorated_func = log_timed_function(ignore_instant_returns=False)(sample_function)
        decorated_func(5, y=10)

        log_content = functional.read_log()
        assert "Function test_function started with args:" in log_content
        assert "(5,)" in log_content
        assert "{'y': 10}" in log_content

    def test_logs_function_completion(self, sample_function):
        """Test that decorator logs function completion with timing."""
        setup_log_file_and_logger(setup_independent_logging=True)

        decorated_func = log_timed_function(ignore_instant_returns=False)(sample_function)
        decorated_func(5)

        log_content = functional.read_log()
        assert "Function test_function finished" in log_content
        assert "seconds" in log_content

    def test_logs_statistics(self, sample_function):
        """Test that decorator logs statistics information."""
        setup_log_file_and_logger(setup_independent_logging=True)

        decorated_func = log_timed_function(ignore_instant_returns=False)(sample_function)
        decorated_func(5)

        log_content = functional.read_log()
        assert "Avg time:" in log_content
        assert "Std dev:" in log_content
        assert "Calls:" in log_content

    def test_no_logs_for_instant_returns(self, fast_function):
        """Test that instant returns don't generate completion logs."""
        setup_log_file_and_logger(setup_independent_logging=True)

        with patch("time.time", side_effect=[1000.0, 1000.0001]):  # Very fast
            decorated_func = log_timed_function(ignore_instant_returns=True)(fast_function)
            decorated_func(5)

        log_content = functional.read_log()
        # Should have start log but not completion/stats logs
        assert "Function fast_test_function started" in log_content
        assert "Function fast_test_function finished" not in log_content

    def test_external_logger_integration(self, mock_logger, sample_function):
        """Test integration with external logger."""
        setup_log_file_and_logger(logger=mock_logger)

        decorated_func = log_timed_function(ignore_instant_returns=False)(sample_function)
        decorated_func(5)

        # Verify logger.info was called
        assert mock_logger.info.call_count >= 3  # Start, finish, stats logs

    def test_logs_with_no_setup_warns_appropriately(self, sample_function, captured_output):
        """Test behavior when no logging is set up."""
        # Don't call setup_log_file_and_logger

        decorated_func = log_timed_function(ignore_instant_returns=False)(sample_function)
        decorated_func(5)

        # Should still work but show warning
        assert any("No log file or logger set up!" in line for line in captured_output)


class TestDecoratorEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_decorator_factory_parameters(self):
        """Test decorator factory with various parameter combinations."""
        # Test all parameter combinations
        decorators = [
            log_timed_function(ignore_instant_returns=True),
            log_timed_function(ignore_instant_returns=False),
            log_timed_function(ignore_instant_returns=True, threshold=0.1),
            log_timed_function(ignore_instant_returns=False, threshold=0.001),
        ]

        for decorator in decorators:

            @decorator
            def test_func():
                return True

            assert callable(test_func)

    def test_decorator_with_recursive_function(self):
        """Test decorator with recursive function."""
        setup_log_file_and_logger(setup_independent_logging=True)

        @log_timed_function(ignore_instant_returns=False)
        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n - 1)

        result = factorial(5)
        assert result == 120

        # Should track each recursive call
        assert len(functional._function_stats["factorial"]) == 5

    def test_decorator_with_generator_function(self):
        """Test decorator with generator function."""
        setup_log_file_and_logger(setup_independent_logging=True)

        @log_timed_function(ignore_instant_returns=False)
        def generator_func():
            yield 1
            yield 2
            yield 3

        gen = generator_func()
        items = list(gen)

        assert items == [1, 2, 3]
        assert "generator_func" in functional._function_stats

    def test_decorator_with_class_method(self):
        """Test decorator with class methods."""
        setup_log_file_and_logger(setup_independent_logging=True)

        class TestClass:
            @log_timed_function(ignore_instant_returns=False)
            def instance_method(self, x):
                return x * 2

            @classmethod
            @log_timed_function(ignore_instant_returns=False)
            def class_method(cls, x):
                return x * 3

            @staticmethod
            @log_timed_function(ignore_instant_returns=False)
            def static_method(x):
                return x * 4

        obj = TestClass()

        assert obj.instance_method(5) == 10
        assert TestClass.class_method(5) == 15
        assert TestClass.static_method(5) == 20

        # All should be tracked separately
        assert "instance_method" in functional._function_stats
        assert "class_method" in functional._function_stats
        assert "static_method" in functional._function_stats

    def test_multiple_decorators_same_function(self):
        """Test applying the same decorator multiple times."""
        setup_log_file_and_logger(setup_independent_logging=True)

        @log_timed_function(ignore_instant_returns=False)
        @log_timed_function(ignore_instant_returns=False)
        def double_decorated():
            return 42

        result = double_decorated()
        assert result == 42

        # Should work but may have nested behavior
        assert "double_decorated" in functional._function_stats

    def test_decorator_with_very_long_execution(self):
        """Test decorator with functions that take a long time."""
        setup_log_file_and_logger(setup_independent_logging=True)

        @log_timed_function(ignore_instant_returns=False)
        def long_running_func():
            time.sleep(0.1)  # Simulate long execution
            return "done"

        result = long_running_func()
        assert result == "done"

        # Should track timing correctly
        stats = functional._function_stats["long_running_func"]
        assert len(stats) == 1
        assert stats[0] >= 0.1  # At least 0.1 seconds
