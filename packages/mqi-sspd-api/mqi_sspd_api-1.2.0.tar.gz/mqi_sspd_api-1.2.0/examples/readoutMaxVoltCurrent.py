import sys
sys.path.append("../mqi-api")
from mqi.api import MQI

m = MQI("ws://mqicontroller001", "8080", "username", "password")

maxVoltCurrent = m.get_max_volt_current(1,[]) # get maximum voltage and current for all channels

print(f"Channel 2: Max Voltage= {maxVoltCurrent.channels[2].volt}, Max Current= {maxVoltCurrent.channels[2].current}")