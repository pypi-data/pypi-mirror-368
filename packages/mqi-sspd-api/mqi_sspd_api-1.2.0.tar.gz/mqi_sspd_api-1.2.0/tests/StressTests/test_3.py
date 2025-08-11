import sys
import threading
import time
import logging
from logging.handlers import RotatingFileHandler
from typing import List
import psutil
sys.path.append("../mqi-api")
from mqi.api import MQI

# Configuration
HOSTNAME = 'ws://localhost'
PORT = '8080'
USERNAME = 'username'
PASSWORD = 'password'
BIASBOX_ID = 1
CHANNEL_IDS = [1, 2, 3]
VALUE = 1.23
TEST_DURATION_HOURS = 6  # duration of soak test
INTERVAL_SECONDS = 5      # time between requests per thread
THREAD_COUNT = 2          # parallel clients

# Setup logger
def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        "stress_test_3.log", maxBytes=5 * 1024 * 1024, backupCount=3
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

logger = setup_logger("stress_test_3")

class SoakTestStats:
    def __init__(self):
        self.success_count = 0
        self.fail_count = 0
        self.lock = threading.Lock()

    def record_success(self):
        with self.lock:
            self.success_count += 1

    def record_failure(self):
        with self.lock:
            self.fail_count += 1

    def get_summary(self):
        with self.lock:
            return self.success_count, self.fail_count

def log_system_usage(prefix=""):
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory().percent
    logger.info(f"{prefix}CPU: {cpu:.1f}%, RAM: {mem:.1f}%")

def soak_worker(stats: SoakTestStats, end_time: float):
    try:
        mqi = MQI(HOSTNAME, PORT, USERNAME, PASSWORD)
    except Exception as e:
        logger.exception("Failed to initialize MQI")
        stats.record_failure()
        return

    while time.time() < end_time:
        try:
            mqi.get_status(BIASBOX_ID)
            mqi.set_current(BIASBOX_ID, CHANNEL_IDS, VALUE)
            mqi.set_voltage(BIASBOX_ID, CHANNEL_IDS, VALUE)
            stats.record_success()
            logger.debug("Successful iteration")
        except Exception as e:
            stats.record_failure()
            logger.error(f"Request failed: {e}")
        log_system_usage(prefix="[Worker] ")
        time.sleep(INTERVAL_SECONDS)


def run_soak_test():
    logger.info("Starting soak test")
    stats = SoakTestStats()
    end_time = time.time() + TEST_DURATION_HOURS * 3600
    threads: List[threading.Thread] = []

    for i in range(THREAD_COUNT):
        t = threading.Thread(target=soak_worker, name=f"SoakThread-{i+1}", args=(stats, end_time), daemon=True)
        threads.append(t)
        t.start()
        logger.debug(f"Started thread {t.name}")

    for t in threads:
        t.join()

    logger.info("Soak test completed")
    success, failures = stats.get_summary()
    logger.info(f"Total Success: {success}, Total Failures: {failures}")
    print(f"Total Success: {success}, Total Failures: {failures}")

if __name__ == '__main__':
    run_soak_test()
