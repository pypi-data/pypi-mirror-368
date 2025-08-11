import sys
import threading
import time
import statistics
import logging
from logging.handlers import RotatingFileHandler
from typing import List, Dict, Any
import psutil
sys.path.append("../mqi-api")
from mqi.api import MQI

# Test configuration
duration_sec = 30
threads_count = 2
hostname = 'ws://10,162.242.63'
port = '8080'
username = 'username'
password = 'password'
biasbox_id = 1
channel_ids = [1, 2, 3]
value = 1.23

# Logger setup
def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        "stress_test_2.log", maxBytes=5 * 1024 * 1024, backupCount=3
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

logger = setup_logger("stress_test_2")

class ThroughputResult:
    def __init__(self):
        self.lock = threading.Lock()
        self.timestamps: List[float] = []
        self.errors: List[str] = []

    def record_success(self) -> None:
        with self.lock:
            self.timestamps.append(time.time())

    def record_error(self, err: Exception) -> None:
        with self.lock:
            msg = repr(err)
            self.errors.append(msg)
            logger.error(f'Recorded error: {msg}')

def log_metrics(prefix: str = '') -> None:
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory().percent
    logger.info(f'{prefix} CPU={cpu:.1f}% RAM={mem:.1f}%')

def worker(result: ThroughputResult, end_time: float) -> None:
    try:
        mqi = MQI(hostname, port, username, password)
    except Exception:
        logger.exception('Connection/authentication failed')
        return

    while time.time() < end_time:
        start = time.perf_counter()
        try:
            mqi.get_status(biasbox_id)
            mqi.set_current(biasbox_id, channel_ids, value)
            mqi.set_voltage(biasbox_id, channel_ids, value)
            result.record_success()
        except Exception as e:
            result.record_error(e)
        finally:
            latency = time.perf_counter() - start
            logger.debug(f'Iteration latency: {latency:.4f}s')

def run_test() -> None:
    result = ThroughputResult()
    end_time = time.time() + duration_sec
    logger.info(f'Starting test: {threads_count} threads for {duration_sec}s')
    log_metrics('[Setup] ')

    threads = [threading.Thread(target=worker, name=f'Worker-{i+1}', args=(result, end_time), daemon=True)
               for i in range(threads_count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    log_metrics('[Teardown] ')

    total = len(result.timestamps)
    errors = len(result.errors)
    avg_rps = total / duration_sec
    peak_rps = 0
    if result.timestamps:
        start_ts = min(result.timestamps)
        counts: Dict[int,int] = {}
        for ts in result.timestamps:
            sec = int(ts - start_ts)
            counts[sec] = counts.get(sec, 0) + 1
        peak_rps = max(counts.values())

    summary = (
        f'Total Success={total}, Errors={errors}\n'
        f'Configured Duration={duration_sec}s, Avg RPS={avg_rps:.2f}, Peak RPS={peak_rps}\n'
    )
    logger.info('Test Summary:\n' + summary)
    print('--- Detailed Throughput Report ---')
    print(summary)

    if errors:
        counts: Dict[str,int] = {}
        for e in result.errors: counts[e] = counts.get(e, 0) + 1
        for err, cnt in counts.items():
            logger.info(f'{err}: {cnt}')
            print(f'{err}: {cnt}')

if __name__ == '__main__':
    run_test()