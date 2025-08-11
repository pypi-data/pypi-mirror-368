# OpenLog

A versatile Python logging utility (overengineered python-rich wrapping) designed to enhance logging capabilities with
rich console output and optional file logging.

## Features

- 🎨 **Rich Console Output**: Color-coded messages with beautiful formatting
- 📁 **Flexible File Logging**: Optional file output with session support
- 🔧 **Task Management**: Progress-bars, special task logging etc.
- 📊 **Multiple Log Levels**: INFO, ERROR, WARN, and INIT with distinct styling
- 💾 **In-Memory Storage**: Retrieve and manage logs programmatically
- 🎯 **Prefix Support**: Add context to your log messages
- 📐 **Terminal-Aware**: Automatic width detection for optimal formatting

## Installation

```bash
pip install openlog
```

## Quick Start

### Basic Console Logging

```python
from openlog import Logger

logger = Logger()
logger.log("This is an info message")
logger.error("Something went wrong")
logger.warn("This is a warning")
logger.init("System initialized")
```

### Batch Logging

```python
# Add multiple messages

logger.batch.add_message("Processing started")
logger.batch.add_message("Loading configuration")
logger.batch.add_message("Connecting to database")

# Log all messages in the batch
logger.flush_batch()
```

### File Logging

```python
# Basic file logging
file_logger = Logger(write_to_file=True)
file_logger.log("This message goes to console and file")

# Session-based logging (timestamped files)
session_logger = Logger(write_to_file=True, session=True)
session_logger.log("Logged with timestamp in filename")

# Organized in /logs directory
dir_logger = Logger(in_dir=True, write_to_file=True)
dir_logger.log("Logs stored in /logs directory")
```

### Task Management

OpenLog supports tracking long-running tasks with animated progress bars:

```python
logger = Logger()

# Start a task with progress bar
task_id = logger.add_task("Processing large dataset")

# Your long-running code here
# ...

# Stop the task
logger.stop_task(task_id)
```

#### Task Management Methods:

- add_task(task_message) - Start a task with progress display
- stop_task(task_id) - Stop a specific task
- get_active_tasks() - Get all currently running tasks
- stop_all_tasks() - Stop all active tasks (useful for cleanup)

### Smart Object Formatting

```python
# Simple objects stay inline
logger.log({"user": "Alice", "id": 123})

# Complex objects format vertically
complex_data = {
    "users": [
        {"id": 1, "name": "Alice", "roles": ["admin", "user"]},
        {"id": 2, "name": "Bob", "roles": ["user", "viewer"]},
    ],
    "settings": {
        "theme": "dark",
        "notifications": {"email": True, "push": False}
    }
}
logger.log("User data:")
logger.log(complex_data)
```

### Retrieve Logs Programmatically

```python
# Get recent logs
logs = logger.flush_logs()

# Get all logs from start
all_logs = logger.flush_logs(from_start=True)
```

## Documentation

For detailed information about all features, configuration options, and advanced usage, see [FEATURES.md](FEATURES.md).

## Configuration

| Parameter       | Type | Default | Description                     |
|-----------------|------|---------|---------------------------------|
| `write_to_file` | bool | False   | Enable file logging             |
| `in_dir`        | bool | False   | Store logs in `/logs` directory |
| `session`       | bool | False   | Create timestamped log files    |
| `prefix`        | str  | ""      | Add prefix to all messages      |

#### Log Levels and Methods

- `log()` - General information (blue)
- `error()` - Error messages (red)
- `warn()` - Warning messages (yellow)
- `init()` - Initialization messages (purple)

#### Batch Operations

- `add_to_batch()` - Add message to batch
- `flush_batch()` - Output all batched messages
- `clear_batch()` - Clear batch without output
- `batch_size()` - Get number of messages in batch

#### Task Management

- `add_task()` - Start task with progress bar
- `stop_task()` - Stop specific task
- `get_active_tasks()` - Get active task information
- `stop_all_tasks()` - Stop all tasks and cleanup

## Requirements

- Python 3.9+
- Rich library (automatically installed)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- [GitHub Repository](https://github.com/Hexerpowers/openlog)
- [Detailed Features Documentation](FEATURES.md)
