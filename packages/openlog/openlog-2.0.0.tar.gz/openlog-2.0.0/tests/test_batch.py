from openlog import Logger

print("=== Testing Batch Functionality ===")

# Create logger for batch testing
batch_logger = Logger(prefix="BATCH")

print("\n--- Adding messages to batch ---")
batch_logger.add_to_batch("First message in batch")
batch_logger.add_to_batch("Second message in batch")
batch_logger.add_to_batch("Third message with a very long text that should be wrapped automatically when the batch is flushed")
batch_logger.add_to_batch("Fourth message")

print(f"Current batch size: {batch_logger.batch_size()}")

print("\n--- Flushing batch as INFO ---")
batch_logger.flush_batch("INFO")

print("\n--- Adding more messages and flushing as ERROR ---")
batch_logger.add_to_batch("Error message 1")
batch_logger.add_to_batch("Error message 2")
batch_logger.add_to_batch("This is a very long error message that demonstrates how the batch system works with text wrapping functionality")

batch_logger.flush_batch("ERROR")

print("\n--- Testing clear batch ---")
batch_logger.add_to_batch("This message will be cleared")
batch_logger.add_to_batch("This one too")
print(f"Batch size before clear: {batch_logger.batch_size()}")
batch_logger.clear_batch()
print(f"Batch size after clear: {batch_logger.batch_size()}")

print("\n--- Mixed usage: regular logging and batch ---")
batch_logger.log("Regular log message")
batch_logger.add_to_batch("Batched message 1")
batch_logger.warn("Regular warning")
batch_logger.add_to_batch("Batched message 2")
batch_logger.flush_batch("WARN")
batch_logger.error("Regular error message")
