import sys
import logging
import threading
import time
from logging.handlers import RotatingFileHandler
from typing import List, Dict
sys.path.append("../mqi-api")
from mqi.api import MQI
import psutil

# Configuration
HOSTNAME = 'ws://localhost'
PORT = '8080'
USERNAME = 'username'
PASSWORD = 'password'
THREADS = 4
DURATION_SEC = 60

# Logger setup
def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        "stress_test_7.log", maxBytes=5 * 1024 * 1024, backupCount=3
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

logger = setup_logger("stress_test_7")

class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.success = 0
        self.errors: Dict[str, int] = {}

    def record_success(self):
        with self.lock:
            self.success += 1

    def record_error(self, err: Exception):
        msg = type(err).__name__ + ": " + str(err)
        with self.lock:
            self.errors[msg] = self.errors.get(msg, 0) + 1

    def summary(self):
        with self.lock:
            return self.success, dict(self.errors)

# Command execution list
def extra_commands(mqi: MQI):
    mqi.get_controlunit_voltages()
    mqi.get_controlunit_temperatures()
    mqi.get_list_of_serial_connections()
   
    mqi.activate_controlunit_fan(True)
    mqi.get_biasbox_temperatures(1)
    mqi.activate_biasbox_fan(1, True)
    mqi.get_biasbox_voltchecker(1)

# Worker thread
def worker(end_time: float, stats: Stats):
    try:
        mqi = MQI(HOSTNAME, PORT, USERNAME, PASSWORD)
    except Exception as e:
        logger.exception("Failed to initialize MQI")
        stats.record_error(e)
        return

    while time.time() < end_time:
        try:
            extra_commands(mqi)
            stats.record_success()
            logger.debug("Executed extra commands successfully")
        except Exception as e:
            logger.error(f"Command error: {e}")
            stats.record_error(e)
        time.sleep(0.5)

# System monitoring
def log_metrics():
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory().percent
    logger.info(f"System CPU: {cpu:.1f}%, RAM: {mem:.1f}%")

# Main runner
def run_load_test():
    logger.info("Starting additional command load test")
    end_time = time.time() + DURATION_SEC
    stats = Stats()
    threads: List[threading.Thread] = []

    for i in range(THREADS):
        t = threading.Thread(target=worker, name=f"CmdThread-{i+1}", args=(end_time, stats), daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    log_metrics()

    success, errors = stats.summary()
    logger.info("Additional command load test complete")
    logger.info(f"Total successful command batches: {success}")
    logger.info(f"Total errors: {sum(errors.values())}")

    print("\n--- Test Summary ---")
    print(f"Successful command batches: {success}")
    print(f"Total errors: {sum(errors.values())}")
    if errors:
        print("Error breakdown:")
        for err, count in errors.items():
            print(f" - {err}: {count}")
            logger.info(f"{err}: {count}")

if __name__ == '__main__':
    run_load_test()