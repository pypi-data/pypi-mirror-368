from openlog import Logger

print("=== Testing Smart Object Formatting (20% threshold for nested) ===")

# Create logger for object testing
obj_logger = Logger(prefix="SMART")

print("\n--- Testing short nested objects (should stay inline) ---")

# Dictionary with short nested objects
short_nested_dict = {
    "user": {"id": 1, "name": "Alice"},
    "settings": {"theme": "dark", "lang": "en"},
    "tags": ["admin", "user"],
    "coords": (10, 20)
}

obj_logger.log("Dict with short nested objects (should keep some inline):")
obj_logger.log(short_nested_dict)

print("\n--- Testing mixed short and long nested objects ---")

mixed_dict = {
    "short_list": [1, 2, 3],
    "long_list": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "short_dict": {"a": 1, "b": 2},
    "long_dict": {
        "name": "Very Long Name That Exceeds Threshold",
        "description": "A very long description that should trigger vertical formatting",
        "metadata": {"created": "2024", "updated": "2024"}
    }
}

obj_logger.warn("Mixed short and long nested objects:")
obj_logger.warn(mixed_dict)

print("\n--- Testing deeply nested with smart formatting ---")

smart_nested = {
    "config": {
        "db": {"host": "localhost", "port": 5432},  # Short, should be inline
        "cache": {
            "redis_host": "redis.example.com",
            "redis_port": 6379,
            "timeout": 30,
            "max_connections": 100,
            "retry_policy": {"max_retries": 3, "backoff": "exponential"}
        },  # Long, should be vertical
        "features": ["auth", "logging", "metrics"]  # Medium, depends on threshold
    },
    "users": [
        {"id": 1, "role": "admin"},  # Short, should be inline
        {
            "id": 2,
            "role": "user",
            "permissions": ["read", "write", "delete"],
            "profile": {"name": "Long User Name", "email": "user@example.com"}
        }  # Long, should be vertical
    ]
}

obj_logger.error("Smart nested formatting:")
obj_logger.error(smart_nested)

print("\n--- Testing edge cases ---")

# Single element containers
single_element_cases = {
    "single_dict": {},
    "single_list": [],
    "single_tuple": (),
    "single_set": set(),
    "single_string": "",
    "single_number": 0,
    "single_bool": False,
    "single_none": None
}

obj_logger.log("Single element containers:")
obj_logger.log(single_element_cases)
