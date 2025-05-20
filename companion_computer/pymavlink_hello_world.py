import sys
import os
import time
import random
import serial
from datetime import datetime
import csv
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from scipy.signal import lombscargle # Not used in this part
import warnings

from broadband_probe_helper_functions import read_and_send_data, read_raw_probe_and_burst_analysis # Import warnings module

# Add the parent directory (where "Drone" resides) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the Drone class from Drone/Drone.py
from Drone.Drone import Drone

# Connect to the vehicle via serial or UDP (adjust as needed)
# connection_string = 'tcp:172.17.240.253:5762'  # Adjust for your setup
# connection_string = 'tcp:192.168.0.124:5762'  # local ip address windows when SITL MP
# connection_string = "udp:127.0.0.1:14560" #when WSL
# connection_string = "tcp:127.0.0.1:5762"
connection_string = "/dev/serial0"
drone = Drone(connection_string,source_system=1,source_component=2,baudrate=57600)

broadband_probe = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

drone.send_message(f"PI:waiting for correct flightmode")
print("waiting for correct flightmode...")
while drone.get_flight_mode()!=4:# see https://ardupilot.org/copter/docs/parameters.html#fltmode1 for flightmodes
    time.sleep(0.2) 

drone.send_message("PI:waiting for heading!")
heading = None
while heading==None:
    time.sleep(1)
    heading = drone.get_heading()
print(heading)
# we have drone heading
drone.send_message(f"PI:heading {heading} received!")
time.sleep(3)
drone.send_message("PI:waiting for grid")

forward=None
right=None
while forward==None and right==None:
    time.sleep(1)
    msg = drone.connection.recv_match(type="STATUSTEXT",blocking=True)
    if msg.get_srcSystem()==2:
        if msg.get_type() == "STATUSTEXT":
            text = msg.to_dict()["text"]
            print(f"received message: {text}")
            if "fw" in text:
                forward = int(text[text.find(":")+1:text.find(" ")])
                right = int(text[text.find(" ")+4:])

print(forward,right)
drone.send_message(f"PI:grid {forward} {right}")
time.sleep(3)
drone.send_message(f"PI:waiting for correct flightmode")

print("waiting for correct flightmode...")
while drone.get_flight_mode()!=4:# see https://ardupilot.org/copter/docs/parameters.html#fltmode1 for flightmodes
    time.sleep(0.2) 

# wait for arming
drone.arm()

# now flightmode is set, takeoff
drone.takeoff(target_altitude=1.5)
time.sleep(5)

drone.set_target_velocity(0.1)


# build and fly local horizontal grid
for f in range(0,forward+1):
    msg = drone.get_global_position()
    if msg:
        current_lat = msg.lat / 1e7
        current_lon = msg.lon / 1e7
        current_alt = msg.relative_alt / 1000.0  # Convert mm to meters
        read_and_send_data(drone,broadband_probe,current_lat,current_lon)
    for r in range(0,right):
        if (f+1)%2:
            drone.fly_to_location_frd_blocking(heading,forward=0,right=1)
        else:
            drone.fly_to_location_frd_blocking(heading,forward=0,right=-1)
        msg = drone.get_global_target_position()
        if msg:
            target_lat = msg.lat_int / 1e7
            target_lon = msg.lon_int / 1e7
            target_alt = msg.alt / 1000.0  # Convert mm to meters
            read_and_send_data(drone,broadband_probe,target_lat,target_lon)
    drone.fly_to_location_frd_blocking(heading,forward=1,right=0)


drone.send_message("PI: done!")

print("mission finished, waiting for user")
# Continuously read MAVLink messages
while True:
    # Wait for a MAVLink message
    msg = drone.connection.recv_match(type="STATUSTEXT",blocking=True)
    if msg.get_srcSystem()==2:
        print("received a message from backend!")
        # Print the received message type and content
        # print(f"Received message: {msg.get_type()}")
        if msg.get_type() == "STATUSTEXT":
            text = msg.to_dict()["text"]
            print(text)
            if "lat" in text:
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
                        read_and_send_data(drone,broadband_probe,current_lat,current_lon)
                        time.sleep(5)
                    for i in range(2):
                        drone.fly_to_location_ned_blocking(0,0.5)#right
                        time.sleep(5)
                        msg = drone.get_global_position()
                        if msg:
                            current_lat = msg.lat / 1e7
                            current_lon = msg.lon / 1e7
                            read_and_send_data(drone,broadband_probe,current_lat,current_lon)

drone.return_home_blocking()
drone.sleep()