# aub kijk hier voor docs en doorklikken op links: https://ardupilot.org/dev/docs/mavlink-commands.html
from pymavlink import mavutil
import time
import random
import math

class Drone:
    def __init__(self, connection_string):
        # Establish connection to the drone using pymavlink
        print(f"Connecting to vehicle on: {connection_string}")
        self.connection = mavutil.mavlink_connection(connection_string)
        self.connection.wait_heartbeat()
        print("Heartbeat received. Drone is ready.")


    # Function to request mission waypoints from the vehicle
    def download_mission(self):
        print("Requesting mission waypoints from the vehicle...")
        self.connection.waypoint_request_list_send()
        waypoints = []

        # Wait for MISSION_COUNT
        msg = self.connection.recv_match(type='MISSION_COUNT', blocking=True)
        if not msg:
            print("Failed to receive MISSION_COUNT.")
            return waypoints

        num_waypoints = msg.count
        print(f"Mission has {num_waypoints} waypoints.")

        for seq in range(num_waypoints):
            # Request each mission item
            self.connection.mav.mission_request_int_send(
                self.connection.target_system,
                self.connection.target_component,
                seq
            )

            # Wait for MISSION_ITEM_INT response
            msg = self.connection.recv_match(type='MISSION_ITEM_INT', blocking=True, timeout=5)
            if msg and msg.get_type() == 'MISSION_ITEM_INT':
                lat = msg.x / 1e7
                lon = msg.y / 1e7
                alt = msg.z
                waypoints.append((lat, lon, alt))
                print(f"Received waypoint {seq}: lat={lat}, lon={lon}, alt={alt}m")
            else:
                print(f"Failed to receive waypoint {seq}.")
                break

        return waypoints[2:] #first is home waypoint second is do speed so don't add to flight
        # Function to calculate the distance between two GPS coordinates

    # Function to request GLOBAL_POSITION_INT message
    def request_global_position_int(self):
        print("Requesting GLOBAL_POSITION_INT...")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,
            0,          # Confirmation
            33,         # ID for GLOBAL_POSITION_INT
            0, 0, 0, 0, 0, 0  # Unused parameters
        )

    def get_global_position(self):
        self.request_global_position_int()
        msg = self.connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        return msg

    def get_flight_mode(self):
        for i in range(5):#try 5 times because also receive heartbeat of GCS
            msg = self.connection.recv_match(type='HEARTBEAT', blocking=True)
            if msg.type==2: #drone
                print(msg)
                print(f"current flight mode: {msg.custom_mode}")
                return msg.custom_mode
        return -1

    def _haversine_distance(self,lat1, lon1, lat2, lon2):
        R = 6371e3  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c *100  # Distance in cm

    def set_flight_mode(self,flightmode):
        # see https://ardupilot.org/copter/docs/parameters.html#fltmode1 for flightmodes
        print(f"Setting mode to {flightmode}...")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE,
            0,
            1,  # MAV_MODE_FLAG_CUSTOM_MODE_ENABLED
            flightmode,  # Custom mode: 
            0, 0, 0, 0, 0
        )

    def arm(self):
        print("-- Arming motors")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1, 0, 0, 0, 0, 0, 0  # Arm the system
        )
        self.connection.motors_armed_wait()
        print("Drone armed")
    
    def takeoff(self,target_altitude=2): 
        # drone should be armed and in guided mode for this to work!
        print("-- Taking off")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0, 0, 0, 0, 0, 0, target_altitude
        )
        # wait for takeoff to finish
        while True:
            msg = self.get_global_position()
            current_alt = msg.relative_alt / 1000.0  # Convert mm to meters
            print(f"Altitude: {current_alt:.2f} m")
            if current_alt >= target_altitude * 0.95:
                print("Reached target altitude")
                break
            time.sleep(1)
    
    def get_distance_from_target(self,target_lat,target_lon,target_alt):
        while True:
            msg = self.get_global_position()
            if msg:
                current_lat = msg.lat / 1e7
                current_lon = msg.lon / 1e7
                current_alt = msg.relative_alt / 1000.0  # Convert mm to meters

                distance = self._haversine_distance(current_lat, current_lon, target_lat, target_lon)
                print(f"Current Position: Lat: {current_lat}, Lon: {current_lon}, Alt: {current_alt:.2f} m")
                print(f"Distance to Target: {distance:.2f} cm")
                return distance
            else:
                print("Waiting for GLOBAL_POSITION_INT...")
                time.sleep(1)

    
    def set_target_velocity(self,target_speed):
        print(f"Settigng target velocity to {target_speed} m/s")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,
            0,            # Confirmation
            1,            # Speed type (0=airspeed, 1=ground speed)
            target_speed, # Target speed in m/s
            -1,           # Throttle (not used, set to -1)
            0, 0, 0, 0    # Unused parameters
        )

    # Function to fly to a specific location
    def fly_to_location(self,lat, lon, alt):
        print(f"Flying to {lat}, {lon} at altitude {alt} meters")
        self.connection.mav.set_position_target_global_int_send(
            0,
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_TERRAIN_ALT_INT, #alt is in meters above terrain
            int(0b110111111000),  # Mask to indicate which dimensions should be ignored https://ardupilot.org/dev/docs/copter-commands-in-guided-mode.html
            int(lat * 1e7),
            int(lon * 1e7),
            alt,
            0, 0, 0,  # x, y, z velocity (not used)
            0, 0, 0,  # afx, afy, afz (not used)
            0, 0      # yaw, yaw rate (not used)
        )

        while True:
            # Check if the drone is within an acceptable range of the target (e.g., 10 centimeters)
            distance = self.get_distance_from_target(lat,lon,alt)
            if distance < 10:
                print("Reached target location")
                break  
            time.sleep(1)

    # Function to send random data to the GCS
    def send_measurement_data(self,lat,lon,alt,value):
        
        print(f"Sending random data: {value}")
        self.connection.mav.statustext_send(
            mavutil.mavlink.MAV_SEVERITY_INFO,
            f"{{\"lat\":{lat}, \"lon\":{lon}, \"RF_Value\":{value}}}".encode('utf-8'),0,0
        )
    def return_home(self):
        print("-- Returning home")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
            0,
            0, 0, 0, 0, 0, 0, 0
        )

        while True:
            msg = self.get_global_position()
            current_alt = msg.relative_alt / 1000.0  # Convert millimeters to meters
            if current_alt <= 0.2:  # 20 cm threshold for landing
                print("Landed successfully")
                break
            time.sleep(2)
    
    def sleep(self):
        print("Closing connection")
        self.connection.close()

if __name__ == "__main__":
    # Connect to the vehicle via serial or UDP (adjust as needed)
    connection_string = 'tcp:172.17.240.253:5762'  # Adjust for your setup
    drone = Drone(connection_string)

    waypoints = drone.download_mission()
    if not waypoints:
        print("No waypoints received!")
        exit()
    
    while drone.get_flight_mode()!=4:# see https://ardupilot.org/copter/docs/parameters.html#fltmode1 for flightmodes
        print("waiting for correct flightmode...")
        time.sleep(0.2)

    # wait for arming
    drone.arm()

    # now flightmode is set, takeoff
    drone.takeoff(target_altitude=2)

    # # set speed does not seem to work
    drone.set_target_velocity(0.1)

    # complete the mission
    for waypoint in waypoints:
        # this is a blocking call and we continue after reaching this point
        drone.fly_to_location(*waypoint)
        print("-- Hovering at point, starting measurements")
        # time.sleep(5)  # Simulate hover and time to take measurement
        # Send random data to the ground control station
        random_number = random.randint(1, 100)
        drone.send_measurement_data(*waypoint,random_number)

    drone.return_home()
    drone.sleep()
