from openlog import Logger

# Basic console-only logger
logger = Logger()
logger.log("This is an info message")
logger.error("Something went wrong")
logger.warn("This is a warning")
logger.init("System initialized")

logger.log("Starting batch operation")
logger.log([
    "Step 1: Validation",
    "Step 2: Processing",
    "Step 3: Cleanup"
])
logger.log("Batch operation completed")

warnings = [
    "High memory usage detected",
    "Cache size approaching limit",
    "Consider increasing memory allocation"
]
logger.warn(warnings)

# Logger with prefix (no need for manual brackets)
prefix_logger = Logger(prefix="APP")
prefix_logger.log("This is an info message with prefix")
prefix_logger.error("Something went wrong with prefix")

# Logger with short timestamp
short_timestamp_logger = Logger(short_timestamp=True)
short_timestamp_logger.log("This message has short timestamp")
short_timestamp_logger.error("Error with short timestamp")


