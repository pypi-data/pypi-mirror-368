import sys
import time
sys.path.append("../mqi-api")
from mqi.api import MQI

m = MQI("ws://mqicontroller001", "8080", "username", "password")

channel_id = [1,3,4] #list of channels to set as active, rest are set as inactive.
biasbox_nr = 1

m.set_channels_active(biasbox_nr, channel_id)

active_channels = m.get_channels_active(biasbox_nr)
print(f"Active channels for Biasbox {biasbox_nr}: {active_channels}")

active_channels.active_channels.append(5) # add channel 5 to activate, rest of the channels are not activated

m.set_channels_active(1, active_channels.active_channels)

print(f"Active channels for Biasbox {biasbox_nr}: {m.get_channels_active(biasbox_nr)}")