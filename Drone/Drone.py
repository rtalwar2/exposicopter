# aub kijk hier voor docs en doorklikken op links: https://ardupilot.org/dev/docs/mavlink-commands.html
from pymavlink import mavutil
import time
import random
import math

class Drone:
    def __init__(self, connection_string, source_system,source_component, baudrate=115200):
        # Establish connection to the drone using pymavlink
        print(f"Connecting to vehicle on: {connection_string}")
        self.connection = mavutil.mavlink_connection(device=connection_string,baud=baudrate,
                                        source_system=source_system,
                                        source_component=source_component)
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

        return waypoints[1:] #first is home waypoint don't add that


    # Function to request GLOBAL_POSITION_INT message
    def request_global_target_position_int(self):
        print("Requesting POSITION_TARGET_GLOBAL_INT...")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,
            0,          # Confirmation
            87,         # ID for POSITION_TARGET_GLOBAL_INT
            0, 0, 0, 0, 0, 0  # Unused parameters
        )

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

    def get_global_target_position(self):
            self.request_global_target_position_int()
            msg = self.connection.recv_match(type='POSITION_TARGET_GLOBAL_INT', blocking=True)
            return msg

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
        self.connection.arducopter_arm()

        # self.connection.mav.command_long_send(
        #     self.connection.target_system,
        #     self.connection.target_component,
        #     mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        #     0,
        #     1, 0, 0, 0, 0, 0, 0  # Arm the system
        # )
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

        

    # Function to fly to a specific location
    def fly_to_location_blocking(self,lat, lon, alt):
        self.fly_to_location(lat, lon, alt)
        while True:
            # Check if the drone is within an acceptable range of the target (e.g., 10 centimeters)
            distance = self.get_distance_from_target(lat,lon,alt)
            if distance < 5:
                print("Reached target location")
                break  
            time.sleep(1)


    def fly_to_location_ned(self, north, east, down=0):

        print(f"Flying to NED position: North={north}m, East={east}m, Down={down}m")
        # Send position target in NED coordinates
        self.connection.mav.set_position_target_local_ned_send(
            0,
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_OFFSET_NED,  # NED coordinate frame
            int(0b110111111000),  # Position mask (consider x, y, z; ignore velocities/acceleration)
            north,  # North position
            east,   # East position
            down,   # Down position
            0, 0, 0,  # x, y, z velocity (not used here)
            0, 0, 0,  # x, y, z acceleration (not used here)
            0, 0     # Yaw, yaw rate (not used here)
        )

    def convert_forward_right_to_ned(self,heading_deg, forward, right):
        heading_rad = math.radians(heading_deg)

        # Forward/right to North/East
        north = forward * math.cos(heading_rad) + right * math.cos(heading_rad+math.pi/2)
        east = forward * math.cos(heading_rad-math.pi/2) + right * math.cos(heading_rad)

        print(f"Converted (forward={forward}m, right={right}m) to (north={north:.2f}m, east={east:.2f}m)")
        return north, east

    def fly_to_location_frd_blocking(self,starting_heading,forward,right):
        north,east = self.convert_forward_right_to_ned(starting_heading,forward,right)
        self.fly_to_location_ned_blocking(north,east)

    def fly_to_location_ned_blocking(self, north, east, down=0):

        self.fly_to_location_ned(north, east, down)
        # Retrieve the target location from POSITION_TARGET_GLOBAL_INT
        target_lat = None
        target_lon = None
        target_alt = None
        while target_lat is None:
            msg = self.get_global_target_position()
            if msg:
                target_lat = msg.lat_int / 1e7
                target_lon = msg.lon_int / 1e7
                target_alt = msg.alt / 1000.0  # Convert mm to meters
                print(f"Target Global Position: Lat={target_lat}, Lon={target_lon}, Alt={target_alt}")

        # Monitor movement until target is reached within tolerance
        while True:
            # Check if the drone is within an acceptable range of the target (e.g., 10 centimeters)
            distance = self.get_distance_from_target(target_lat,target_lon,1.5)
            if distance < 5:
                print("Reached target location")
                break  
            time.sleep(1)



    # Function to send random data to the GCS
    def send_measurement_data(self,lat,lon,alt,value):
        print(f"Sending data: {value}")
        self.connection.mav.statustext_send(
            mavutil.mavlink.MAV_SEVERITY_INFO,
            f"{{\"lat\":{lat}, \"lon\":{lon}, \"V\":{value}}}".encode('utf-8'),0,0
        )

    def send_message(self,message):
        print(f"Sending message: {message}")
        self.connection.mav.statustext_send(
            mavutil.mavlink.MAV_SEVERITY_INFO,
            message.encode('utf-8'),0,0
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

    def return_home_blocking(self):
        self.return_home()
        while True:
            msg = self.get_global_position()
            current_alt = msg.relative_alt / 1000.0  # Convert millimeters to meters
            if current_alt <= 0.2:  # 20 cm threshold for landing
                print("Landed successfully")
                break
            time.sleep(2)
        
    def get_heading(self):
        msg = self.get_global_position()
        if msg and hasattr(msg, 'hdg'):
            heading = msg.hdg / 100.0  # heading in degrees (0-360°)
            print(f"Current heading: {heading}°")
            return heading
        else:
            print("Failed to get heading.")
            return None
    

    def sleep(self):
        print("Closing connection")
        self.connection.arducopter_disarm()
        self.connection.close()

    def test_motor_spin_individual(self, motor_index, throttle_rpm, duration_seconds):

        print(f"Spinning motor {motor_index} at {throttle_rpm} RPM for {duration_seconds} seconds.")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,  
            0,  # Confirmation
            motor_index,  # Motor index (0-based)
            1,  # Motor test throttle type (1 = RPM control, see ArduPilot docs)
            throttle_rpm,  # Desired throttle/RPM
            duration_seconds,  # Duration in seconds
            1, # Motor Count
            0, # Test order
            0  # Unused parameter
        )
    
    def test_motor_spin_all(self,throttle_rpm,duration_seconds=60):
        # Spin motors sequentially
        for motor_index in range(1, 5):
            self.test_motor_spin_individual(motor_index, throttle_rpm, duration_seconds)
            time.sleep(0.01)
        
    def test_motor_spin_all_increasing(self,min,max,step_duration,total_duration):

        for i in range(min,max,(max-min)//total_duration):
            self.test_motor_spin_all(i,step_duration+5)
            time.sleep(step_duration)


    def request_distance_sensor(self):
        print("Requesting DISTANCE_SENSOR message...")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,
            0,         # Confirmation
            132,       # Message ID for DISTANCE_SENSOR
            0, 0, 0, 0, 0, 0
        )

    def get_sonar_range(self):
        """
        Retrieves the current sonar/rangefinder distance from the drone (in meters).
        """
        print("Requesting sonar range (DISTANCE_SENSOR)...")
        
        self.request_distance_sensor()

        msg = self.connection.recv_match(type='DISTANCE_SENSOR', blocking=True)
        if msg:
            distance_m = msg.current_distance / 100.0  # Convert from cm to meters
            print(f"Sonar range: {distance_m:.2f} meters")
            return distance_m
        else:
            print("No DISTANCE_SENSOR message received.")
            return None
