import sys
import threading
import time
import logging
from logging.handlers import RotatingFileHandler
from typing import List
sys.path.append("../mqi-api")
from mqi.api import MQI
import psutil

# Configuration
HOSTNAME = 'ws://localhost'
PORT = '8080'
USERNAME = 'username'
PASSWORD = 'password'
BIASBOX_ID = 1
CHANNEL_IDS = [1, 2, 3]
VALUE = 1.23
RETRY_DELAY = 5  # seconds
MAX_RETRIES = 3

# Logger setup
def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        "stress_test_4.log", maxBytes=5 * 1024 * 1024, backupCount=3
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

logger = setup_logger("stress_test_4")

class RecoveryTestResult:
    def __init__(self):
        self.success_count = 0
        self.failure_count = 0
        self.recovery_count = 0
        self.lock = threading.Lock()

    def record_success(self):
        with self.lock:
            self.success_count += 1

    def record_failure(self):
        with self.lock:
            self.failure_count += 1

    def record_recovery(self):
        with self.lock:
            self.recovery_count += 1

    def summary(self):
        with self.lock:
            return self.success_count, self.failure_count, self.recovery_count

def log_system_metrics():
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    logger.info(f"System metrics - CPU: {cpu:.1f}%, RAM: {ram:.1f}%")

def perform_actions(mqi: MQI):
    mqi.get_status(BIASBOX_ID)
    mqi.set_current(BIASBOX_ID, CHANNEL_IDS, VALUE)
    mqi.set_voltage(BIASBOX_ID, CHANNEL_IDS, VALUE)

def recovery_test():
    result = RecoveryTestResult()
    logger.info("Starting error recovery test")
    
    for cycle in range(10):
        logger.info(f"Test cycle {cycle + 1}/10")
        try:
            mqi = MQI(HOSTNAME, PORT, USERNAME, PASSWORD)
        except Exception as e:
            logger.exception("Initial connection failed")
            result.record_failure()
            continue

        try:
            perform_actions(mqi)
            result.record_success()
            logger.info("Initial actions successful")
        except Exception as e:
            logger.warning(f"Initial action failed: {e}")
            result.record_failure()
            logger.info("Attempting recovery")

            for attempt in range(1, MAX_RETRIES + 1):
                logger.info(f"Recovery attempt {attempt}/{MAX_RETRIES}")
                time.sleep(RETRY_DELAY)
                try:
                    mqi = MQI(HOSTNAME, PORT, USERNAME, PASSWORD)
                    perform_actions(mqi)
                    result.record_recovery()
                    logger.info("Recovery successful")
                    break
                except Exception as retry_error:
                    logger.warning(f"Recovery attempt {attempt} failed: {retry_error}")
                    if attempt == MAX_RETRIES:
                        result.record_failure()

        log_system_metrics()
        time.sleep(2)

    success, failures, recoveries = result.summary()
    summary = (
        f"Error Recovery Test Complete:\n"
        f"  Successes: {success}\n"
        f"  Failures: {failures}\n"
        f"  Recoveries: {recoveries}\n"
    )
    logger.info(summary)
    print(summary)

if __name__ == '__main__':
    recovery_test()