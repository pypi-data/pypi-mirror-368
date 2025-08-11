import sys
import threading
import time
import statistics
import logging
from logging.handlers import RotatingFileHandler
from typing import List
import psutil  # for system metrics
sys.path.append("../mqi-api")
from mqi.api import MQI

# Configure detailed logging for stress test
def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        "stress_test_1.log", maxBytes=5 * 1024 * 1024, backupCount=3
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

logger = setup_logger("stress_test_1")

class StressTestResult:
    def __init__(self):
        self.latencies: List[float] = []
        self.errors: List[str] = []
        self.lock = threading.Lock()

    def record_success(self, latency: float):
        with self.lock:
            self.latencies.append(latency)
            logger.debug(f"Recorded success latency: {latency:.4f} sec")

    def record_error(self, error: Exception):
        with self.lock:
            err_msg = repr(error)
            self.errors.append(err_msg)
            logger.error(f"Recorded error: {err_msg}")


def log_system_metrics(prefix: str = ""):
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory().percent
    logger.info(f"{prefix}System metrics - CPU: {cpu:.1f}%, RAM: {mem:.1f}%")


def worker(hostname: str, port: str, username: str, password: str, results: StressTestResult):
    thread_name = threading.current_thread().name
    logger.info(f"[{thread_name}] Starting connection to {hostname}:{port} as {username}")
    log_system_metrics(prefix=f"[{thread_name}] Before auth - ")
    start = time.perf_counter()
    try:
        mqi = MQI(hostname, port, username, password)
        latency = time.perf_counter() - start
        results.record_success(latency)
        logger.info(f"[{thread_name}] Authentication succeeded in {latency:.4f} sec")
        log_system_metrics(prefix=f"[{thread_name}] After auth - ")
    except Exception as e:
        latency = time.perf_counter() - start
        results.record_error(e)
        logger.exception(f"[{thread_name}] Authentication failed after {latency:.4f} sec")
        log_system_metrics(prefix=f"[{thread_name}] After failure - ")


def run_stress_test(hostname: str,
                    port: str,
                    username: str,
                    password: str,
                    concurrent_clients: int):
    logger.info(f"Starting stress test: {concurrent_clients} concurrent clients")
    log_system_metrics(prefix="[Main] Before test - ")
    results = StressTestResult()
    threads: List[threading.Thread] = []

    for i in range(concurrent_clients):
        t = threading.Thread(
            target=worker,
            name=f"ClientThread-{i+1}",
            args=(hostname, port, username, password, results),
            daemon=True
        )
        threads.append(t)
        t.start()
        logger.debug(f"Started thread {t.name}")

    for t in threads:
        t.join()
        logger.debug(f"Thread {t.name} finished")

    log_system_metrics(prefix="[Main] After test - ")

    total = len(results.latencies) + len(results.errors)
    success = len(results.latencies)
    failures = len(results.errors)
    avg_latency = statistics.mean(results.latencies) if success else 0
    median = statistics.median(results.latencies) if success else 0
    p95 = sorted(results.latencies)[int(0.95 * success) - 1] if success else 0
    p99 = sorted(results.latencies)[int(0.99 * success) - 1] if success else 0

    summary = (
        f"Stress Test Complete: Total={total}, Success={success}, Failures={failures}, "
        f"Avg Latency={avg_latency:.4f} sec, p50={median:.4f} sec, "
        f"p95={p95:.4f} sec, p99={p99:.4f} sec"
    )
    logger.info(summary)
    print(summary)

    if failures:
        logger.info("Sample errors:")
        print("Sample errors:")
        for err in results.errors[:5]:
            print(f" - {err}")
            logger.info(f" - {err}")


def main():
    HOSTNAME = 'ws://localhost'
    PORT = '8080'
    USERNAME = 'username'
    PASSWORD = 'password'
    CLIENTS = 200

    start_time = time.time()
    run_stress_test(HOSTNAME, PORT, USERNAME, PASSWORD, CLIENTS)
    duration = time.time() - start_time
    logger.info(f"Total stress test duration: {duration:.4f} sec")
    print(f"Total stress test duration: {duration:.4f} sec")

if __name__ == '__main__':
    main()
