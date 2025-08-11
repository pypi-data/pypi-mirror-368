import sys
import time
sys.path.append("../mqi-api")
from mqi.api import MQI

m = MQI("ws://mqicontroller001", "8080", "username", "password")

# temperature inside the biasbox
print(m.get_BiasBox_temperatures(1))
# example of showing the voltage which applied to the biasbox
print(m.get_BiasBox_voltchecker(1))
