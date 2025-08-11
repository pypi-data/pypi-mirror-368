import sys
import numpy as np

sys.path.append("../mqi-api")
import time
from mqi.api import MQI

m = MQI("ws://mqicontroller001", "8080", "username", "password")

channel_id = [] # Empty list to set voltage on all channels
biasbox_nr = 1

voltage = 0.1 # Volt
print(f"Setting voltage to {voltage} A")
m.set_voltage(biasbox_nr, channel_id, voltage)
time.sleep(0.5)  # Wait for the voltage to stabilize
measured_voltage = m.get_voltage(1, channel_id)
print(
    f"Voltage for Biasbox {biasbox_nr}, channel 1: "
    f"setVoltage:{measured_voltage.channels[1].value_set}, "
    f"measuredVoltage:{measured_voltage.channels[1].value_get}"
)