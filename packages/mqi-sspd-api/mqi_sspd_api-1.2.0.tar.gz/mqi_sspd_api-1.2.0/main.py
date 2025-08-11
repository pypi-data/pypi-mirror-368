from mqi.v1.api import MQI 
from websocket import create_connection 
import time

def float_range(start, stop, step):
    current = start
    while current < stop:
        yield current
        current += step

m = MQI("ws://mqicontroller001", "8080")
m.connect()
print("status", m.getStatus(0))
#print("setCurrentWorked=",m.setCurrent(0,2,2.2))



for i in float_range(0.0, 2.4, 0.1):
    m.setCurrent(0,8,i)
    time.sleep(0.5)
    print(m.getAdcBias(0)[0][2:4])


m.setCurrent(0,8,0)
time.sleep(10)
print(m.getAdcBias(0))
