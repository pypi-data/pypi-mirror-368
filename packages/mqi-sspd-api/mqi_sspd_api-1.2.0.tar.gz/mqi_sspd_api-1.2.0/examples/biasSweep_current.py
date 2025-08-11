import sys
import numpy as np
import time
sys.path.append("../mqi-api")
from mqi.api import MQI

m = MQI("ws://mqicontroller001", "8080", "username", "password")

channel_id = [1,2]
biasbox_nr = 1



for current in np.arange(0, 0.0001, 0.00001): 
    print(f"Setting voltage to {current} A")
    m.set_current(biasbox_nr, channel_id, current)
    time.sleep(0.5)  # Wait for the voltage to stabilize
    adc_voltage = m.get_current(1, channel_id)
    print(f"Current for Biasbox {biasbox_nr}, Channel 2: {adc_voltage.channels[2].value}")
    print("-" * 40)