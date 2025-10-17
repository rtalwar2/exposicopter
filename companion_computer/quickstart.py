import sys
import os
import time
import random
# Add the parent directory (where "Drone" resides) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the Drone class from Drone/Drone.py
from Drone.Drone import Drone

# Connect to the vehicle via serial or UDP (adjust as needed)
# connection_string = 'tcp:172.17.240.253:5762'  # Adjust for your setup
# connection_string = 'tcp:192.168.0.124:5762'  # local ip address windows when SITL MP
connection_string = "tcp:127.0.0.1:5762" #when wsl
drone = Drone(connection_string,source_system=1,source_component=2)
drone.send_message(f"PI:Hello world!")

time.sleep(3)
drone.set_flight_mode(4)

# wait for arming
drone.arm()

# now flightmode is set, takeoff
drone.takeoff(target_altitude=2)

drone.fly_to_location_ned(north=50,east=2)
# the blocking version relies on POSITION_TARGET_GLOBAL_INT being updated but after summer POSITION_TARGET_LOCAL_NED should be used to get target location
time.sleep(5)
drone.fly_to_location_ned(north=-20,east=-4)
time.sleep(5)

drone.return_home_blocking()
drone.sleep()