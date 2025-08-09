# Isolated Logging

A Python library for performance monitoring and optimization through detailed execution timing, statistics tracking, and color-coded logging.

## Features

- **🎯 Function Timing**: Decorator-based automatic timing with statistics tracking
- **🔄 Loop Performance**: Monitor iterations with progress tracking and ETA calculation
- **⚡ Parallel Processing**: Built-in parallel loop execution with timing
- **📊 Rich Statistics**: Track averages, standard deviations, and execution patterns
- **🎨 Color-Coded Output**: Enhanced readability with ANSI color support
- **📍 Checkpoint System**: Named checkpoints for tracking execution milestones
- **📝 Flexible Logging**: Output to file, external logger, or stdout

## Installation

### From PyPI (when available)
```bash
pip install isolated-logging
```

### From Source
```bash
git clone https://github.com/jurrutiag/isolated-logging.git
cd isolated-logging
pip install -e .
```

### With Optional Dependencies
```bash
# For parallel processing support
pip install "isolated-logging[parallel]"

# For development
pip install "isolated-logging[testing]"
```

## Quick Start

```python
import time
from isolated_logging import (
    setup_log_file_and_logger,
    log_timed_function,
    log_timed_loop,
    log_message,
    log_checkpoint
)

# Initialize logging
setup_log_file_and_logger(setup_independent_logging=True)

# Time a function with automatic statistics
@log_timed_function(threshold=0.01)
def process_item(item):
    time.sleep(0.1)
    return item * 2

# Monitor loop performance with ETA
items = range(100)
for item in log_timed_loop(items, loop_name="Processing"):
    result = process_item(item)

    # Log intermediate results
    if item % 10 == 0:
        log_message(f"Processed {item} items")
        log_checkpoint(f"batch_{item//10}")
```

## Core Features

### Function Timing

```python
@log_timed_function(
    ignore_instant_returns=True,  # Skip logging for instant returns
    threshold=0.001,              # Only log if execution > threshold
    include_args=True             # Include function arguments in logs
)
def expensive_operation(data):
    # Your code here
    pass
```

### Loop Monitoring

```python
# Basic loop timing with progress
for item in log_timed_loop(items, loop_name="Training"):
    process(item)

# Get iteration statistics
for i, item in enumerate(log_timed_loop(items)):
    if i % 100 == 0:
        stats = get_loop_stats("Loop")
        print(f"Average time: {stats['avg_time']:.4f}s")
```

### Parallel Processing

```python
from isolated_logging import log_timed_parallel_loop

def process_chunk(item):
    # CPU-intensive work
    return item ** 2

# Process in parallel with automatic timing
results = log_timed_parallel_loop(
    items,
    process_chunk,
    n_jobs=4,
    loop_name="Parallel Processing"
)
```

### Checkpoints

```python
log_checkpoint("data_loaded")
# ... some processing ...
log_checkpoint("model_trained")
# ... more processing ...
log_checkpoint("results_saved")

# Get checkpoint statistics
stats = get_checkpoint_stats()
print(f"Time from data_loaded to model_trained: {stats['model_trained']['time_since_last']:.2f}s")
```

### Custom Logging

```python
# Log with colors
from isolated_logging import log_message_with_color, Color

log_message_with_color("Success!", Color.GREEN)
log_message_with_color("Warning!", Color.YELLOW)
log_message_with_color("Error!", Color.RED)

# Use external logger
import logging
logger = logging.getLogger(__name__)
setup_log_file_and_logger(logger=logger)
```

## Advanced Usage

### Retrieving Statistics

```python
from isolated_logging import (
    get_function_stats,
    get_loop_stats,
    get_checkpoint_stats,
    print_all_stats
)

# Get function execution statistics
func_stats = get_function_stats("expensive_operation")
print(f"Called {func_stats['count']} times")
print(f"Average time: {func_stats['avg_time']:.4f}s")

# Get loop performance data
loop_stats = get_loop_stats("Training")
print(f"Total iterations: {loop_stats['count']}")
print(f"Time per iteration: {loop_stats['avg_time']:.4f}s ± {loop_stats['std_time']:.4f}s")

# Print comprehensive statistics
print_all_stats()
```

### Configuration Options

```python
setup_log_file_and_logger(
    logger=custom_logger,           # Use existing logger
    log_file_path="/tmp/perf.log",  # Custom log file location
    setup_independent_logging=True,  # Create independent logger
    log_level=logging.DEBUG,        # Set logging level
    disable_colors=False            # Disable ANSI colors
)
```

## API Reference

### Setup Functions
- `setup_log_file_and_logger()`: Initialize logging system
- `close_log_file()`: Close log file handle

### Timing Decorators & Context Managers
- `@log_timed_function()`: Decorator for function timing
- `log_timed_loop()`: Context manager for loop timing
- `log_timed_parallel_loop()`: Parallel processing with timing

### Logging Functions
- `log_message()`: Log a message
- `log_message_with_color()`: Log with color
- `log_checkpoint()`: Create named checkpoint

### Statistics Functions
- `get_function_stats()`: Retrieve function statistics
- `get_loop_stats()`: Retrieve loop statistics
- `get_checkpoint_stats()`: Retrieve checkpoint data
- `print_all_stats()`: Display all statistics

## Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/jurrutiag/isolated-logging.git
cd isolated-logging

# Install in development mode with test dependencies
pip install -e ".[testing]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests
```bash
# Run all tests with coverage
pytest --cov=isolated_logging

# Run specific test file
pytest tests/test_functional.py

# Run with verbose output
pytest -v
```

### Code Quality
```bash
# Format code
ruff format

# Check linting
ruff check --fix

# Type checking
mypy src/isolated_logging

# Run all pre-commit hooks
pre-commit run --all-files
```

### Building Package
```bash
# Build distribution
python -m build

# Install locally
pip install dist/isolated_logging-*.whl
```

## Requirements

- Python 3.10+
- NumPy (for statistics)
- Loky (optional, for parallel processing)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the [GitHub issue tracker](https://github.com/jurrutiag/isolated-logging/issues).
