import time
from openlog import Logger

# Create logger
logger = Logger()

# Start a task
task_id1 = logger.add_task("Processing data")

# Simulate some work
time.sleep(2)

# Start another task
task_id2 = logger.add_task("Loading files")

# Simulate more work
time.sleep(3)

# Stop first task
logger.stop_task(task_id1)

# Continue with second task
time.sleep(2)

# Stop second task
logger.stop_task(task_id2)

# Example with multiple tasks
logger.log("Starting batch processing")

tasks = []
for i in range(3):
    task_id = logger.add_task(f"Task {i+1}")
    tasks.append(task_id)

# Simulate work and stop tasks one by one
for i, task_id in enumerate(tasks):
    time.sleep(1)
    logger.stop_task(task_id)

logger.log("Batch processing completed")

# Cleanup (optional, but good practice)
logger.stop_all_tasks()
