"""
Comprehensive integration test suite for isolated-logging library.

This module tests the integration between different components of the library,
including real-world usage scenarios, complex workflows, and cross-feature interactions.
"""

import time
from unittest.mock import Mock

import isolated_logging.functional as functional
from isolated_logging import (
    log_checkpoint,
    log_list_elements,
    log_message,
    log_message_with_color,
    log_timed_function,
    log_timed_loop,
    log_timed_parallel_loop,
    setup_log_file_and_logger,
)
from isolated_logging.functional import Color


class TestCompleteWorkflow:
    """Tests for complete workflow scenarios using multiple features."""

    def test_data_processing_workflow(self):
        """Test a complete data processing workflow using multiple features."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Start with checkpoint
        log_checkpoint("workflow_start", "Beginning data processing workflow")

        # Log workflow parameters
        log_message("Starting data processing workflow")
        processing_params = ["batch_size: 100", "workers: 4", "timeout: 30s"]
        log_list_elements(processing_params)

        # Define processing function with decorator
        @log_timed_function(ignore_instant_returns=True, threshold=0.001)
        def process_item(item):
            # Simulate processing time
            time.sleep(0.01)
            return item.upper()

        # Process data with timed loop
        input_data = ["item1", "item2", "item3"]
        results = []

        for item in log_timed_loop(input_data, loop_name="DataProcessing"):
            result = process_item(item)
            results.append(result)

        # Mark completion checkpoint
        log_checkpoint("workflow_start", "Data processing completed")

        # Verify results
        assert results == ["ITEM1", "ITEM2", "ITEM3"]

        # Verify all components logged correctly
        log_content = functional.read_log()

        # Should contain checkpoint messages
        assert "Beginning data processing workflow" in log_content
        assert "Data processing completed" in log_content

        # Should contain workflow messages
        assert "Starting data processing workflow" in log_content
        assert "batch_size: 100" in log_content

        # Should contain loop information
        assert "(DataProcessing)" in log_content

        # Should contain function timing
        assert "process_item" in log_content

    def test_machine_learning_training_simulation(self):
        """Test simulation of machine learning training workflow."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Training configuration
        log_message_with_color("ML Training Configuration", Color.CYAN)
        config = {"epochs": 3, "batch_size": 32, "learning_rate": 0.001, "model": "neural_network"}
        log_list_elements([f"{k}: {v}" for k, v in config.items()])

        # Training function
        @log_timed_function(ignore_instant_returns=False)
        def train_epoch(epoch_num, data_batches):
            # Simulate training time
            time.sleep(0.02)
            return {"epoch": epoch_num, "loss": 1.0 / (epoch_num + 1)}

        # Training loop with checkpoints
        epochs = range(1, config["epochs"] + 1)
        training_results = []

        log_checkpoint("training_start", "Starting ML training")

        for epoch in log_timed_loop(epochs, loop_name="TrainingLoop"):
            log_checkpoint(f"epoch_{epoch}", f"Starting epoch {epoch}")

            # Simulate data batches
            batches = list(range(5))  # 5 batches per epoch

            result = train_epoch(epoch, batches)
            training_results.append(result)

            log_message_with_color(
                f"Epoch {epoch} completed with loss: {result['loss']:.4f}", Color.GREEN
            )

            log_checkpoint(f"epoch_{epoch}", f"Epoch {epoch} completed")

        log_checkpoint("training_start", "ML training completed")

        # Verify training results
        assert len(training_results) == 3
        assert all("loss" in result for result in training_results)

        # Verify comprehensive logging
        log_content = functional.read_log()

        # Should track multiple checkpoints
        assert "Starting ML training" in log_content
        assert "Starting epoch 1" in log_content
        assert "Epoch 1 completed" in log_content

        # Should have statistics for training function
        assert "train_epoch" in log_content
        assert "Avg time:" in log_content

    def test_parallel_data_analysis_workflow(self, monkeypatch):
        """Test parallel data analysis with comprehensive logging."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Mock parallel processing components
        mock_executor = Mock()
        mock_executor.__enter__ = Mock(return_value=mock_executor)
        mock_executor.__exit__ = Mock(return_value=None)

        submitted_futures = []

        def mock_submit(timed_func_arg, func, item, **kwargs):
            # Call the actual timed_func to get proper return format
            mock_future = Mock()
            # timed_func returns (result, elapsed_time, item)
            result = func(item)
            mock_future.result.return_value = (result, 0.5, item)
            submitted_futures.append(mock_future)
            return mock_future

        mock_executor.submit = mock_submit

        monkeypatch.setattr(functional, "get_reusable_executor", Mock(return_value=mock_executor))

        # Mock as_completed to return futures in order
        def mock_as_completed(futures_dict):
            return futures_dict.keys()

        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        # Analysis workflow
        log_checkpoint("analysis_start", "Beginning parallel data analysis")

        log_message_with_color("Analysis Configuration", Color.YELLOW)
        log_list_elements(["workers: 4", "chunk_size: 1000", "algorithm: statistical"])

        # Analysis function
        def analyze_chunk(chunk):
            return f"analyzed_{chunk}"

        # Parallel processing
        data_chunks = ["chunk1", "chunk2", "chunk3"]

        results, errors = log_timed_parallel_loop(
            data_chunks, analyze_chunk, {}, n_jobs=4, loop_name="ParallelAnalysis"
        )

        # Post-processing with decorator
        @log_timed_function(ignore_instant_returns=False)
        def consolidate_results(results_list):
            time.sleep(0.01)  # Simulate consolidation time
            return {"consolidated": len(results_list), "status": "success"}

        final_result = consolidate_results(results)

        log_checkpoint("analysis_start", "Data analysis completed")
        log_message_with_color(f"Analysis complete: {final_result}", Color.GREEN)

        # Verify workflow executed correctly
        assert len(results) == 3  # Should have one result per chunk
        assert errors == []
        assert final_result["status"] == "success"

        # Verify comprehensive logging
        log_content = functional.read_log()
        assert "Beginning parallel data analysis" in log_content
        assert "(ParallelAnalysis)" in log_content
        assert "consolidate_results" in log_content


class TestCrossFeatureInteractions:
    """Tests for interactions between different library features."""

    def test_decorated_function_in_timed_loop(self):
        """Test decorated function called within timed loop."""
        setup_log_file_and_logger(setup_independent_logging=True)

        @log_timed_function(ignore_instant_returns=False)
        def process_with_decoration(item):
            time.sleep(0.01)
            return item * 2

        results = []
        for item in log_timed_loop([1, 2, 3], loop_name="DecoratedProcessing"):
            result = process_with_decoration(item)
            results.append(result)

        assert results == [2, 4, 6]

        # Should have both loop and function statistics
        assert len(functional._loop_stats) > 0
        assert "process_with_decoration" in functional._function_stats

        log_content = functional.read_log()
        assert "(DecoratedProcessing)" in log_content
        assert "process_with_decoration" in log_content

    def test_checkpoints_with_loops_and_functions(self):
        """Test checkpoints used in combination with loops and functions."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_checkpoint("process_start", "Starting multi-stage process")

        @log_timed_function(ignore_instant_returns=False)
        def stage_processor(stage_data):
            time.sleep(0.01)
            return f"processed_{stage_data}"

        # Multi-stage processing
        stages = ["stage1", "stage2", "stage3"]

        for stage in log_timed_loop(stages, loop_name="StageProcessing"):
            log_checkpoint(f"stage_{stage}", f"Starting {stage}")

            stage_processor(stage)

            log_checkpoint(f"stage_{stage}", f"Completed {stage}")

        log_checkpoint("process_start", "Multi-stage process completed")

        # Verify all components tracked separately
        assert "process_start" in functional._checkpoint_stats
        assert "stage_stage1" in functional._checkpoint_stats
        assert "stage_processor" in functional._function_stats
        assert len(functional._loop_stats) > 0

    def test_nested_loops_with_different_configurations(self):
        """Test nested loops with different timing configurations."""
        setup_log_file_and_logger(setup_independent_logging=True)

        outer_data = [1, 2]
        inner_data = ["a", "b"]

        results = []

        for outer in log_timed_loop(
            outer_data, loop_name="OuterLoop", ignore_instant_iterations=False
        ):
            for inner in log_timed_loop(
                inner_data, loop_name="InnerLoop", ignore_instant_iterations=True, threshold=0.001
            ):
                result = f"{outer}{inner}"
                results.append(result)
                time.sleep(0.005)  # Small delay

        assert results == ["1a", "1b", "2a", "2b"]

        # Should have separate statistics for each loop
        assert len(functional._loop_stats) == 2

        log_content = functional.read_log()
        assert "(OuterLoop)" in log_content
        assert "(InnerLoop)" in log_content

    def test_multiple_checkpoint_ids_with_function_stats(self):
        """Test multiple checkpoint IDs alongside function statistics."""
        setup_log_file_and_logger(setup_independent_logging=True)

        @log_timed_function(ignore_instant_returns=False)
        def multi_checkpoint_function(phase):
            log_checkpoint(f"function_{phase}", f"Function processing {phase}")
            time.sleep(0.01)
            return f"result_{phase}"

        # Multiple phases with different checkpoint patterns
        phases = ["initialization", "processing", "cleanup"]

        for phase in phases:
            log_checkpoint("main_flow", f"Starting {phase} phase")
            multi_checkpoint_function(phase)
            log_checkpoint("main_flow", f"Completed {phase} phase")

        # Verify separate tracking
        assert "main_flow" in functional._checkpoint_stats
        assert "function_initialization" in functional._checkpoint_stats
        assert "function_processing" in functional._checkpoint_stats
        assert "function_cleanup" in functional._checkpoint_stats
        assert "multi_checkpoint_function" in functional._function_stats

        # Should have multiple timing measurements
        main_flow_times = functional._checkpoint_stats["main_flow"]["times"]
        assert len(main_flow_times) >= 3  # At least 3 intervals


class TestRealWorldScenarios:
    """Tests simulating real-world usage scenarios."""

    def test_web_scraping_workflow(self, monkeypatch):
        """Test web scraping workflow with error handling."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Mock parallel processing for scraping
        mock_executor = Mock()
        mock_executor.__enter__ = Mock(return_value=mock_executor)
        mock_executor.__exit__ = Mock(return_value=None)
        submitted_futures = []

        def mock_submit(timed_func_arg, func, item, **kwargs):
            mock_future = Mock()
            if "error" in item:
                # Simulate exception during execution
                mock_future.result.side_effect = Exception("Connection timeout")
            else:
                # timed_func returns (result, elapsed_time, item)
                mock_future.result.return_value = (func(item), 1.5, item)
            submitted_futures.append(mock_future)
            return mock_future

        mock_executor.submit = mock_submit

        monkeypatch.setattr(functional, "get_reusable_executor", Mock(return_value=mock_executor))

        # Mock as_completed to return futures in order
        def mock_as_completed(futures_dict):
            return futures_dict.keys()

        monkeypatch.setattr(functional, "as_completed", mock_as_completed)

        log_checkpoint("scraping_start", "Beginning web scraping session")

        # Configuration logging
        log_message_with_color("Web Scraping Configuration", Color.CYAN)
        scraping_config = [
            "concurrent_workers: 5",
            "timeout: 30s",
            "retry_attempts: 3",
            "user_agent: bot_v1.0",
        ]
        log_list_elements(scraping_config)

        # Scraping function
        def scrape_url(url):
            if "error" in url:
                raise Exception("Connection timeout")
            return f"content_from_{url}"

        # URLs to scrape
        urls = ["http://site1.com", "http://error-site.com"]

        # Parallel scraping with error handling
        results, errors = log_timed_parallel_loop(
            urls, scrape_url, {}, n_jobs=2, loop_name="WebScraping", raise_exceptions=False
        )

        # Process results with decorated function
        @log_timed_function(ignore_instant_returns=False)
        def process_scraped_data(data_list):
            time.sleep(0.01)
            return {"processed_items": len(data_list), "success_rate": 0.8}

        if results:
            summary = process_scraped_data(results)
            log_message_with_color(f"Processing summary: {summary}", Color.GREEN)

        log_checkpoint("scraping_start", "Web scraping session completed")

        # Verify error handling
        assert len(results) == 1  # One successful result
        assert len(errors) == 1  # One error

        log_content = functional.read_log()
        assert "Connection timeout" in log_content
        assert "(WebScraping)" in log_content
        assert "Beginning web scraping session" in log_content

    def test_batch_processing_with_monitoring(self):
        """Test batch processing with comprehensive monitoring."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Batch processing setup
        log_checkpoint("batch_start", "Starting batch processing job")

        # Configuration
        batch_config = {
            "input_files": 10,
            "output_format": "json",
            "compression": "gzip",
            "validation": "strict",
        }

        log_message_with_color("Batch Processing Configuration", Color.YELLOW)
        log_list_elements([f"{k}: {v}" for k, v in batch_config.items()])

        # Processing stages with monitoring
        @log_timed_function(ignore_instant_returns=False)
        def validate_input(file_path):
            time.sleep(0.01)  # Simulate validation
            return {"valid": True, "records": 100}

        @log_timed_function(ignore_instant_returns=False)
        def transform_data(file_path):
            time.sleep(0.02)  # Simulate transformation
            return {"transformed_records": 95, "errors": 5}

        @log_timed_function(ignore_instant_returns=False)
        def save_output(data):
            time.sleep(0.01)  # Simulate saving
            return {"saved": True, "output_file": "batch_output.json"}

        # Process multiple files
        input_files = [f"input_{i}.csv" for i in range(3)]
        results = []

        for file_path in log_timed_loop(input_files, loop_name="FileProcessing"):
            # Stage 1: Validation
            log_checkpoint("validation", f"Validating {file_path}")
            validation_result = validate_input(file_path)

            # Stage 2: Transformation
            log_checkpoint("transformation", f"Transforming {file_path}")
            transform_result = transform_data(file_path)

            # Stage 3: Output
            log_checkpoint("output", f"Saving {file_path}")
            save_result = save_output(transform_result)

            results.append(
                {
                    "file": file_path,
                    "validation": validation_result,
                    "transformation": transform_result,
                    "output": save_result,
                }
            )

        log_checkpoint("batch_start", "Batch processing job completed")

        # Final summary
        total_records = sum(r["validation"]["records"] for r in results)
        total_errors = sum(r["transformation"]["errors"] for r in results)

        log_message_with_color(
            f"Batch Summary - Records: {total_records}, Errors: {total_errors}", Color.GREEN
        )

        # Verify comprehensive tracking
        assert len(results) == 3
        assert "validate_input" in functional._function_stats
        assert "transform_data" in functional._function_stats
        assert "save_output" in functional._function_stats

        # Multiple checkpoint IDs should exist
        assert "batch_start" in functional._checkpoint_stats
        assert "validation" in functional._checkpoint_stats
        assert "transformation" in functional._checkpoint_stats
        assert "output" in functional._checkpoint_stats


class TestPerformanceAndScalability:
    """Tests for performance and scalability scenarios."""

    def test_high_volume_logging_performance(self):
        """Test performance with high volume of logging calls."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # High volume scenario
        num_operations = 100

        log_checkpoint("performance_test", "Starting high volume test")

        # Mix of different logging operations
        for i in range(num_operations):
            if i % 10 == 0:
                log_checkpoint(f"batch_{i // 10}", f"Processing batch {i // 10}")

            log_message(f"Operation {i}")

            if i % 5 == 0:
                log_message_with_color(f"Special operation {i}", Color.YELLOW)

            if i % 20 == 0:
                log_list_elements([f"item_{i}_a", f"item_{i}_b"])

        log_checkpoint("performance_test", "High volume test completed")

        # Verify all operations completed
        log_content = functional.read_log()
        assert "Operation 0" in log_content
        assert f"Operation {num_operations - 1}" in log_content
        assert "Starting high volume test" in log_content
        assert "High volume test completed" in log_content

    def test_complex_nested_workflow_performance(self):
        """Test performance with complex nested workflows."""
        setup_log_file_and_logger(setup_independent_logging=True)

        @log_timed_function(ignore_instant_returns=False)
        def complex_calculation(data):
            # Simulate complex calculation
            time.sleep(0.005)
            return sum(data) * 2

        # Nested workflow
        log_checkpoint("complex_workflow", "Starting complex nested workflow")

        outer_range = range(3)  # Outer loop
        inner_range = range(2)  # Inner loop

        total_results = []

        for outer in log_timed_loop(outer_range, loop_name="OuterProcessing"):
            log_checkpoint(f"outer_{outer}", f"Starting outer iteration {outer}")

            outer_results = []

            for inner in log_timed_loop(inner_range, loop_name=f"Inner_{outer}"):
                log_checkpoint(f"inner_{outer}_{inner}", f"Processing {outer}-{inner}")

                # Generate some data
                data = [outer, inner, outer + inner]

                # Complex calculation
                result = complex_calculation(data)
                outer_results.append(result)

                log_checkpoint(f"inner_{outer}_{inner}", f"Completed {outer}-{inner}")

            total_results.extend(outer_results)
            log_checkpoint(f"outer_{outer}", f"Completed outer iteration {outer}")

        log_checkpoint("complex_workflow", "Complex nested workflow completed")

        # Verify results and comprehensive tracking
        assert len(total_results) == 6  # 3 * 2 = 6 results

        # Should have multiple statistics tracked
        assert "complex_calculation" in functional._function_stats
        assert len(functional._loop_stats) >= 2  # Multiple loops
        assert len(functional._checkpoint_stats) >= 5  # Multiple checkpoints

        # Verify comprehensive logging
        log_content = functional.read_log()
        assert "Starting complex nested workflow" in log_content
        assert "OuterProcessing" in log_content
        assert "complex_calculation" in log_content


class TestErrorHandlingIntegration:
    """Tests for error handling across integrated features."""

    def test_error_recovery_workflow(self):
        """Test workflow with error recovery using multiple features."""
        setup_log_file_and_logger(setup_independent_logging=True)

        log_checkpoint("error_recovery", "Starting error recovery test")

        @log_timed_function(ignore_instant_returns=False)
        def potentially_failing_function(item):
            time.sleep(0.01)
            if "error" in item:
                raise ValueError(f"Processing failed for {item}")
            return f"processed_{item}"

        # Data with potential errors
        test_data = ["good1", "error_item", "good2", "good3"]
        successful_results = []
        failed_items = []

        for item in log_timed_loop(test_data, loop_name="ErrorRecovery"):
            log_checkpoint("item_processing", f"Processing {item}")

            try:
                result = potentially_failing_function(item)
                successful_results.append(result)
                log_message_with_color(f"Success: {item}", Color.GREEN)

            except ValueError as e:
                failed_items.append(item)
                log_message_with_color(f"Error: {str(e)}", Color.RED)

            log_checkpoint("item_processing", f"Completed processing {item}")

        # Summary
        log_checkpoint("error_recovery", "Error recovery test completed")

        summary_message = f"Processed: {len(successful_results)}, Failed: {len(failed_items)}"
        log_message_with_color(summary_message, Color.YELLOW)

        # Verify error handling
        assert len(successful_results) == 3  # 3 good items
        assert len(failed_items) == 1  # 1 error item
        assert "processed_good1" in successful_results

        # Function should still have statistics despite errors
        assert "potentially_failing_function" in functional._function_stats

        # Checkpoints should track all attempts
        processing_times = functional._checkpoint_stats["item_processing"]["times"]
        assert len(processing_times) >= 4  # All 4 items processed

    def test_logging_system_resilience(self):
        """Test system resilience when logging components fail."""
        setup_log_file_and_logger(setup_independent_logging=True)

        # Test with file write errors
        original_write = functional._log_file.write
        write_call_count = 0

        def intermittent_failing_write(content):
            nonlocal write_call_count
            write_call_count += 1
            if write_call_count % 3 == 0:  # Fail every 3rd write
                # Silently ignore the write on failure
                return 0
            return original_write(content)

        functional._log_file.write = intermittent_failing_write

        # Attempt normal workflow despite write failures
        log_checkpoint("resilience_test", "Testing system resilience")

        @log_timed_function(ignore_instant_returns=False)
        def resilient_function(x):
            return x * 2

        results = []
        for i in log_timed_loop([1, 2, 3], loop_name="ResilientLoop"):
            result = resilient_function(i)
            results.append(result)

        # Restore original write function
        functional._log_file.write = original_write

        # Core functionality should still work
        assert results == [2, 4, 6]

        # Some statistics should still be tracked
        assert "resilient_function" in functional._function_stats or len(functional._loop_stats) > 0
