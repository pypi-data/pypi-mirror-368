from openlog import Logger

# Logger with file output
file_logger = Logger(write_to_file=True)
file_logger.log("This message goes to console and file")

# Session-based logging (new log file for each session)
session_logger = Logger(write_to_file=True, session=True)
session_logger.log("Logged with timestamp in filename")

# Store logs in a specific directory
dir_logger = Logger(in_dir=True, write_to_file=True)
dir_logger.log("Logs stored in /logs directory")

# Retrieve logs programmatically
logs = file_logger.flush_logs()
all_logs = file_logger.flush_logs(from_start=True)
