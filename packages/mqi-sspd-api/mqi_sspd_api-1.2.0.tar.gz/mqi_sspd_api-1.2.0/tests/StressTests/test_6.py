import logging
from logging.handlers import RotatingFileHandler
import time
import os

# Configuration
NUM_MESSAGES = 20000
MESSAGE_SIZE = 300  # approx. characters per log message

# Setup logger for rotation test
def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        "stress_test_6.log", maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(threadName)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger("stress_test_6")

# Test function to fill logs and trigger rotation
def run_log_rotation_test():
    logger.info("Starting log rotation test")
    sample_payload = "X" * MESSAGE_SIZE

    for i in range(NUM_MESSAGES):
        logger.debug(f"Message {i+1}: {sample_payload}")
        if i % 100 == 0:
            time.sleep(0.01)  # short delay to allow I/O flushing

    logger.info("Log rotation test completed")

    # Summary
    log_files = [f for f in os.listdir('.') if f.startswith("stress_test_6")]
    for f in log_files:
        size = os.path.getsize(f)
        logger.info(f"Log file '{f}': {size / 1024:.2f} KB")
    print(f"Created log files: {log_files}")

if __name__ == '__main__':
    run_log_rotation_test()