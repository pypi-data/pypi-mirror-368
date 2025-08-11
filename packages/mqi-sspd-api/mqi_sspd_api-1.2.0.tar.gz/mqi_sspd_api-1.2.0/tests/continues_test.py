import sys
import os
import time
from itertools import combinations

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from mqi.v1.api import MQI

m = MQI("ws://10.162.242.63", "8080", "username", "password")
# m = MQI("ws://localhost", "8080", "username", "password")

voltage = 0.0  # Start with 0.0
max_voltage = 2.5  # Maximum voltage
step = 0.1  # Voltage increment step
biasbox_ID = 1  # Biasbox ID to use
print(m.get_id(biasbox_ID))
# Generate all combinations of channels from 1 to 8
channels_range = range(1, 9)
channels_combinations = []
for r in range(1, len(channels_range) + 1):
    channels_combinations.extend(combinations(channels_range, r))

# Convert combinations to a list for iteration
channels_combinations = [list(c) for c in channels_combinations]
current_channel_index = 0  # Start with the first combination
for j in range(0,10):
    print(m.get_ControlUnit_voltages())
    for i in range(0, 100):
    # Get the current channel list
        channels = channels_combinations[current_channel_index]

    # Set the voltage for the current channels
        print(m.set_voltage(biasbox_ID, channels, voltage))
        time.sleep(1)

    # Increment the voltage
        voltage += step
        if voltage > max_voltage:
                voltage = 0.0  # Reset voltage if it exceeds max

    # Move to the next channel combination
        current_channel_index += 1
        if current_channel_index >= len(channels_combinations):
                current_channel_index = 0  # Reset channel index if it exceeds available combinations

    # Get the ADC voltage
        for i in range(0, 10):
                print(m.get_voltage(biasbox_ID, []))
        time.sleep(5)
