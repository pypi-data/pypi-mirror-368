import sys
import numpy as np
import time
sys.path.append("../mqi-api")
from mqi.api import MQI

m = MQI("ws://mqicontroller001", "8080", "username", "password")

channel_id = [1,2]
biasbox_nr = 1

current = 0.00001 # Amp
print(f"Setting Current to {current} A")
m.set_current(biasbox_nr, channel_id, current)
time.sleep(0.5)  # Wait for the voltage to stabilize
measured_current = m.get_current(1, channel_id)
print(f"Current for Biasbox {biasbox_nr}, channel 1: {measured_current.channels[1].value}")



