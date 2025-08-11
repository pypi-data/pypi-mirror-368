import sys
import logging
from logging.handlers import RotatingFileHandler
sys.path.append("../mqi-api")
from mqi.api import MQI
from typing import List, Tuple
import time

# Configuration
HOSTNAME = 'ws://localhost'
PORT = '8080'
USERNAME = 'username'
PASSWORD = 'password'
BIASBOX_ID = 1
CHANNEL_IDS = [1, 2, 3]

# Parameter boundaries
CURRENT_VALUES: List[Tuple[str, float]] = [
    ("min", 0.0),
    ("low", 0.01),
    ("nominal", 1.0),
    ("high", 10.0),
    ("max", 20.0),
    ("over", 100.0)
]

VOLTAGE_VALUES: List[Tuple[str, float]] = [
    ("min", 0.0),
    ("low", 0.1),
    ("nominal", 5.0),
    ("high", 30.0),
    ("max", 60.0),
    ("over", 100.0)
]

# Logger setup
def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        "stress_test_5.log", maxBytes=5 * 1024 * 1024, backupCount=3
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

logger = setup_logger("stress_test_5")


def test_boundary_values():
    logger.info("Starting boundary value test")
    try:
        mqi = MQI(HOSTNAME, PORT, USERNAME, PASSWORD)
    except Exception as e:
        logger.exception("Failed to initialize MQI")
        return

    for label, value in CURRENT_VALUES:
        try:
            logger.info(f"Setting current to '{label}' = {value}")
            status, body = mqi.set_current(BIASBOX_ID, CHANNEL_IDS, value)
            logger.info(f"Current set result [{label}]: status={status}, body={body}")
        except Exception as e:
            logger.error(f"Failed to set current [{label}]: {e}")
        time.sleep(0.2)

    for label, value in VOLTAGE_VALUES:
        try:
            logger.info(f"Setting voltage to '{label}' = {value}")
            status, body = mqi.set_voltage(BIASBOX_ID, CHANNEL_IDS, value)
            logger.info(f"Voltage set result [{label}]: status={status}, body={body}")
        except Exception as e:
            logger.error(f"Failed to set voltage [{label}]: {e}")
        time.sleep(0.2)

    logger.info("Boundary value test completed")

if __name__ == '__main__':
    test_boundary_values()