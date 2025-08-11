import sys
import time
sys.path.append("../mqi-api")
from mqi.api import MQI

m = MQI("ws://mqicontroller001", "8080", "username", "password")

m.set_led_brightness(0.5)  # Set LED brightness to 50%