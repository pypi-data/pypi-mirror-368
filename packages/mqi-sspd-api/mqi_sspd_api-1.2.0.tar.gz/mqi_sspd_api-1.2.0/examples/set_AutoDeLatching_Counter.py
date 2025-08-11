import sys
sys.path.append("../mqi-api")
import time 
from mqi.api import MQI

m = MQI("ws://mqicontroller001", "8080", "username", "password")

print(m.get_BiasBox_AutoDelatching(1))

biasbox_nr = 1
activate = True # Whether to activate (True) or deactivate (False) auto-de-latching.
checkLatchingInterval_ms= 5000# Interval (in milliseconds) for checking latch-up conditions.
volt_drop_for_detection = 0.10 # Voltage drop in percent threshold to detect a latch-up in perc of the current voltage.
perc_start_fineSweep = 0.60 # Percentage of previous voltage to start the fine sweep after detection.
roughSteps = 3 # Number of steps for the rough voltage sweep.
fineSteps = 5 # Number of steps for the fine voltage sweep.
sweep_delay_ms =400 # Delay (in milliseconds) between each voltage step during the sweep process.

print(m.set_BiasBox_AutoDelatching(biasbox_nr, activate, checkLatchingInterval_ms, volt_drop_for_detection, perc_start_fineSweep, roughSteps, fineSteps, sweep_delay_ms))

for i in range(10):
    time.sleep(1) 
    print(m.get_BiasBox_AutoDelatching_Counter(1, []))