import sys
import numpy as np
import time
sys.path.append("../mqi-api")
from mqi.api import MQI

m = MQI("ws://mqicontroller001", "8080", "username", "password")

channel_id = [1,2]

for volt in np.arange(0, 1.1, 0.1):
    print(f"Setting voltage to {volt} V")
    m.set_voltage(1, channel_id, volt)
    time.sleep(0.5)  # Wait for the voltage to stabilize
    adc_voltage = m.get_voltage(1, channel_id)
    print(f"ADC Voltage for Biasbox 1: {adc_voltage}")
    print("-" * 40)