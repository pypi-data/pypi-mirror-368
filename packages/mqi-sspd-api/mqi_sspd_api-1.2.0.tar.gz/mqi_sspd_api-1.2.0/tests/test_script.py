import sys
import time
sys.path.append("../mqi-api")
from mqi.v1.api import MQI
import json

def test_mqi_api():
    # Connect to the server with credentials
    print("Connecting to server...")
    biasbox_ID=1
    m = MQI("ws://localhost", "8080", "username", "password", False)
    
    
    print("Connected successfully.\n")

    # Test: Get the number of connected biasboxes
    print("Testing get_numb_of_biasboxes()...")
    biasboxes_count = m.get_number_of_biasboxes()
    print(f"Number of biasboxes: {biasboxes_count}\n")

    # Test: Get status of a specific Biasbox
    print("Testing get_status() for Biasbox ID 1...")
    status = m.get_BiasBox_status(biasbox_ID)
    print(f"Status of Biasbox 1: {status}\n")

    # Test: Set current for specific channels
    print("Testing set_current() for Biasbox ID 1, channels [1, 2], value 5...")
    status  = m.set_current(biasbox_ID, [1, 2], 0.0000005)
    print(f"Set Current Response: {status}\n")

    # Test: Set voltage for specific channels
    print("Testing set_voltage() for Biasbox ID 1, channels [1, 2], value 3...")
    status_set_voltage_response  = m.set_voltage(biasbox_ID, [1, 2,3], 0.1)
    print(f"Set Voltage Response: {status_set_voltage_response}\n")

    # Test: Get number of channels for a specific Biasbox
    print("Testing get_number_of_channels() for Biasbox ID 1...")
    num_channels = m.get_number_of_channels(biasbox_ID)
    print(f"Number of channels on Biasbox 1: {num_channels}\n")

    # Test: Set specific channels active for an Biasbox
    print("Testing set_channels_active() for Biasbox ID 1, channels [1, 2]...")
    set_channels_active_response= m.set_channels_active(biasbox_ID, [1, 2])
    print(f"Set Channels Active Response: {set_channels_active_response}\n")

    # Test: Get active channels for an Biasbox
    print("Testing get_channels_active() for Biasbox ID 1...")
    active_channels = m.get_channels_active(biasbox_ID)
    print(f"Active Channels on Biasbox 1: {active_channels}\n")

    # Test: Get ADC voltage for specific channels
    print("Testing get_voltage() for Biasbox ID 1, channels [1, 2]...")
    adc_voltage = m.get_voltage(biasbox_ID, [1, 2])
    print(f"ADC Voltage for Biasbox 1: {adc_voltage}\n")

    # Test: Get target voltage for specific channels
    print("Testing get_target_voltage() for Biasbox ID 1, channels [1, 2]...")
    target_voltage = m.get_target_voltage(biasbox_ID, [1, 2])
    print(f"target Voltage for Biasbox 1: {target_voltage}\n")

    # Test: Get the maximum voltage and current for Biasbox
    print("Testing get_max_volt_current() for Biasbox ID 1...")
    max_volt_current = m.get_max_volt_current(biasbox_ID,[])
    print(f"Max Voltage and Current for Biasbox 1: {max_volt_current}\n")

    # Test: Restart a specific Biasbox
    # print("Testing restart_Biasbox() for Biasbox ID 1...")
    # restart_response = m.restart_Biasbox(1)
    # print(f"Restart Response for Biasbox 1: {restart_response}\n")

    # Test: Get ID
    print("Testing get_id() for Biasbox ID 1...")
    id = m.get_BiasBox_ID(biasbox_ID)
    print(f"Biasbox ID: {id}\n")

    # Test: Get the configuration of the system
    print("Testing get_config()...")
    config = m.get_config()
    print(f"System Configuration: {config}\n")

    # Test: Set the configuration of the system
    print("Testing set_config() with a sample configuration...")
    set_config_response = m.set_config(config.to_json())
    print(f"Set Config Response: {set_config_response}\n")

    # Test: Set LED color
    print("Testing set_led_brightness() to set LED color...")
    led_color_response = m.set_led_brightness(0.5)
    print(f"Set LED Color Response: {led_color_response}\n")

    # Test: Activate control unit fan
    print("Testing activate_cu_fan() to activate fan...")
    fan_response = m.activate_ControlUnit_fan(True)
    print(f"Activate CU Fan Response: {fan_response}\n")

    # Test: Get BiasBox temperatures
    print("Testing get_BiasBox_temperatures() for Biasbox ID 1...")
    biasbox_temps = m.get_BiasBox_temperatures(1)
    print(f"BiasBox Temperatures: {biasbox_temps}\n")

    # Test: Get BiasBox voltage checker
    print("Testing get_BiasBox_voltchecker() for Biasbox ID 1...")
    biasbox_voltchecker = m.get_BiasBox_voltchecker(1)
    print(f"BiasBox Voltage Checker: {biasbox_voltchecker}\n")

    # Final Test: Restart Raspberry Pi
    # print("Testing restart_rpi()...")
    rpi_restart_response = m.restart_rpi()
    print(f"Raspberry Pi Restart Response: {rpi_restart_response}\n")

if __name__ == "__main__":
    test_mqi_api()