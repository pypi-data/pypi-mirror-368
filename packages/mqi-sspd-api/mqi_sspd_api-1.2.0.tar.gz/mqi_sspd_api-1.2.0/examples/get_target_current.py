import sys

sys.path.append("../mqi-api")
from mqi.api import MQI

m = MQI("ws://mqicontroller001", "8080", "username", "password")

# Example usage of get the set current on channel 1 and 2
target_current = m.get_target_current(1, [1, 2])

print(target_current.channels[1])
# Example usage of get the set current on all channels
target_current = m.get_target_current(1, [])
