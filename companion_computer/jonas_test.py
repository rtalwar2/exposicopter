import sys
import os
import time
import serial
import csv
import threading
from datetime import datetime

# Add the parent directory (where "Drone" resides) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the Drone class from Drone/Drone.py
from Drone.Drone import Drone

# Setup drone connection
connection_string = "/dev/serial0"
drone = Drone(connection_string, source_system=1, source_component=2, baudrate=57600)

test_duration=35
# drone.test_motor_spin_all_increasing(1070, 1300, 1, total_duration=test_duration)
drone.test_motor_spin_all(2000,test_duration)

time.sleep(test_duration)
drone.sleep()