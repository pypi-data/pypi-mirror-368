# SiMPLe Logger

A simple logging library with colored output and file rotation support

## Installation

```bash
pip install smpl-logger
```

Or install from source:

```bash
pip install git+https://github.com/greengoblinalex/simple-logger.git
```

## Usage

```python
from smpl_logger import get_logger

# It is recommended to use __name__ as the logger name —
# this is convenient for structuring logs in large projects
logger = get_logger(__name__)

# You can also explicitly pass a string, for example:
# logger = get_logger("my_app")
logger.info("This is an info message")
logger.error("This is an error message")

# Logging to file and console
file_logger = get_logger(__name__, log_file="app.log")
file_logger.info("This message will appear in both file and console")
```

## Configuration

You can configure the logger using additional parameters:

```python
logger = get_logger(
    name=__name__,  # Recommended to use __name__, but you can use a string
    log_file="app.log",
    level="DEBUG",  # Logging level
    rotation_size=5 * 1024 * 1024,  # 5 MB for rotation
    backup_count=3  # Keep 3 backup files
)
```

## Configuration via .env file

You can also configure logging parameters via a `.env` file in your project root:

```
LOG_DIR=logs                # Directory for log files
LOG_LEVEL=INFO              # Logging level
LOG_ROTATION_SIZE=5242880   # File size for rotation (5MB)
LOG_BACKUP_COUNT=3          # Number of backup files
```

## Features

- 🎨 **Colored output** - different log levels are highlighted with different colors
- 🔄 **File rotation** - automatic log rotation when the file reaches the maximum size
- ⚙️ **Flexible configuration** - configure via function parameters or environment variables
- 📦 **Lightweight** - no external dependencies, uses only the Python standard library
- 🔧 **Easy to use** - minimal code to get started

## Example of colored output

When using console logging, you will see:
- 🟢 **INFO** - green for informational messages
- 🟡 **WARNING** - yellow for warnings
- 🔴 **ERROR** - red for errors
- 🔵 **DEBUG** - cyan for debug information
- 🟥 **CRITICAL** - red background for critical errors