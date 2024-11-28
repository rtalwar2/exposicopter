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
# connection_string = "udp:127.0.0.1:14560" #when WSL
connection_string = "tcp:127.0.0.1:5762"
drone = Drone(connection_string,source_system=1,source_component=2)

waypoints = drone.download_mission()
if not waypoints:
    print("No waypoints received!")
    # exit()

while drone.get_flight_mode()!=4:# see https://ardupilot.org/copter/docs/parameters.html#fltmode1 for flightmodes
    print("waiting for correct flightmode...")
    time.sleep(0.2) 

# wait for arming
drone.arm()

# now flightmode is set, takeoff
drone.takeoff(target_altitude=2)

# # set speed sometimes works sometimes doesn't todo, check!
drone.set_target_velocity(0.1)

# complete the mission
for waypoint in waypoints:
    # this is a blocking call and we continue after reaching this point
    drone.fly_to_location_blocking(*waypoint)

    print("-- Hovering at point, starting measurements")
    time.sleep(5)  # Simulate hover and time to take measurement
    # Send random data to the ground control station
    random_number = random.randint(1, 100)
    drone.send_measurement_data(*waypoint,random_number)

print("mission finished, waiting for user")
# Continuously read MAVLink messages
while True:
    # Wait for a MAVLink message
    msg = drone.connection.recv_match(type="STATUSTEXT",blocking=True)
    # msg = mavlink_connection.recv_match(blocking=True)
    if msg.get_srcSystem()==3:
        print("received a message from backend!")
        # Print the received message type and content
        # print(f"Received message: {msg.get_type()}")
        if msg.get_type() == "STATUSTEXT":
            text = msg.to_dict()["text"]
            print(text)
            lat = text[text.find(":")+1:text.find(" ")]
            lon = text[text.find(" ")+5:]
            drone.fly_to_location_blocking(float(lat),float(lon),1.5)
            drone.fly_to_location_ned_blocking(1,0.5)#up
            for j in range(3):
                drone.fly_to_location_ned_blocking(-0.5,-1)#up
                msg = drone.get_global_position()
                if msg:
                    current_lat = msg.lat / 1e7
                    current_lon = msg.lon / 1e7
                    drone.send_measurement_data(current_lat,current_lon,1.5,5)
                for i in range(2):
                    drone.fly_to_location_ned_blocking(0,0.5)#right
                    time.sleep(5)
                    msg = drone.get_global_position()
                    if msg:
                        current_lat = msg.lat / 1e7
                        current_lon = msg.lon / 1e7
                        drone.send_measurement_data(current_lat,current_lon,1.5,5)

drone.return_home_blocking()
drone.sleep()
