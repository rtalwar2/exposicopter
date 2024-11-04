# aub kijk hier voor docs en doorklikken op links: https://ardupilot.org/dev/docs/mavlink-commands.html
from pymavlink import mavutil
import time
import random
import math

# Connect to the vehicle via serial or UDP (adjust as needed)
connection_string = 'tcp:192.168.129.7:5762'  # Adjust for your setup
print(f"Connecting to vehicle on: {connection_string}")
master = mavutil.mavlink_connection(connection_string)
master.wait_heartbeat()
print("Heartbeat received. Vehicle connected!")

# Function to request mission waypoints from the vehicle
def download_mission():
    print("Requesting mission waypoints from the vehicle...")
    master.waypoint_request_list_send()
    waypoints = []

    # Wait for MISSION_COUNT
    msg = master.recv_match(type='MISSION_COUNT', blocking=True)
    if not msg:
        print("Failed to receive MISSION_COUNT.")
        return waypoints

    num_waypoints = msg.count
    print(f"Mission has {num_waypoints} waypoints.")

    for seq in range(num_waypoints):
        # Request each mission item
        master.mav.mission_request_int_send(
            master.target_system,
            master.target_component,
            seq
        )

        # Wait for MISSION_ITEM_INT response
        msg = master.recv_match(type='MISSION_ITEM_INT', blocking=True, timeout=5)
        if msg and msg.get_type() == 'MISSION_ITEM_INT':
            lat = msg.x / 1e7
            lon = msg.y / 1e7
            alt = msg.z
            waypoints.append((lat, lon, alt))
            print(f"Received waypoint {seq}: lat={lat}, lon={lon}, alt={alt}m")
        else:
            print(f"Failed to receive waypoint {seq}.")
            break

    return waypoints[1:] #first is home waypoint so don't add to flight


# Function to calculate the distance between two GPS coordinates
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371e3  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c *100  # Distance in cm


# Function to request GLOBAL_POSITION_INT message
def request_global_position_int():
    print("Requesting GLOBAL_POSITION_INT...")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,
        0,          # Confirmation
        33,         # ID for GLOBAL_POSITION_INT
        0, 0, 0, 0, 0, 0  # Unused parameters
    )

def set_mode_to_guided():
    print("Setting mode to GUIDED...")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE,
        0,
        1,  # MAV_MODE_FLAG_CUSTOM_MODE_ENABLED
        4,  # Custom mode: GUIDED
        0, 0, 0, 0, 0
    )

    # Wait for confirmation
    while True:
        msg = master.recv_match(type='HEARTBEAT', blocking=True)
        if msg and msg.custom_mode == 4:  # Confirm mode change to GUIDED
            print("Mode set to GUIDED")
            break



# Function to arm the vehicle and take off
def arm_and_takeoff(target_altitude=2): #https://ardupilot.org/dev/docs/mavlink-arming-and-disarming.html
    # Set the mode to GUIDED
    set_mode_to_guided()

    print("-- Arming motors")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1, 0, 0, 0, 0, 0, 0  # Arm the system
    )
    master.motors_armed_wait()
    print("Vehicle armed")

    print("-- Taking off")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,
        0, 0, 0, 0, 0, 0, target_altitude
    )


    while True:
        request_global_position_int()
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        current_alt = msg.relative_alt / 1000.0  # Convert millimeters to meters
        print(f"Altitude: {current_alt:.2f} m")
        if current_alt >= target_altitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

# Function to fly to a specific location
def fly_to_location(lat, lon, alt):
    print(f"Flying to {lat}, {lon} at altitude {alt} meters")
    master.mav.set_position_target_global_int_send(
        0,
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_FRAME_GLOBAL_TERRAIN_ALT_INT, #alt is in meters above terrain
        int(0b110111111000),  # Mask to indicate which dimensions should be ignored
        int(lat * 1e7),
        int(lon * 1e7),
        alt,
        0, 0, 0,  # x, y, z velocity (not used)
        0, 0, 0,  # afx, afy, afz (not used)
        0, 0      # yaw, yaw rate (not used)
    )

    while True:
        request_global_position_int()
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        if msg:
            current_lat = msg.lat / 1e7
            current_lon = msg.lon / 1e7
            current_alt = msg.relative_alt / 1000.0  # Convert mm to meters

            distance = haversine_distance(current_lat, current_lon, lat, lon)

            print(f"Current Position: Lat: {current_lat}, Lon: {current_lon}, Alt: {current_alt:.2f} m")
            print(f"Distance to Target: {distance:.2f} cm")

            # Check if the drone is within an acceptable range of the target (e.g., 10 centimeters)
            if distance < 10:
                print("Reached target location")
                break  
            time.sleep(1) 
        else:
            print("Waiting for GLOBAL_POSITION_INT...")
            time.sleep(1)

# Function to send random data to the GCS
def send_random_data(lat,lon,alt):
    random_number = random.randint(1, 100)
    print(f"Sending random data: {random_number}")
    master.mav.statustext_send(
        mavutil.mavlink.MAV_SEVERITY_INFO,
        f"{{\"lat\":{lat}, \"lon\":{lon}, \"RF_Value\":{random_number}}}".encode('utf-8'),0,0
    )

# Main
try:
    waypoints = download_mission()
    if not waypoints:
        print("No waypoints received!")
        exit()

    arm_and_takeoff(2)  # Replace with desired takeoff altitude

    for waypoint in waypoints:
        fly_to_location(*waypoint)
        print("-- Hovering at point, starting measurements")
        time.sleep(5)  # Simulate hover and time to take measurement
        # Send random data to the ground control station
        send_random_data(*waypoint)

    print("-- Returning home")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
        0,
        0, 0, 0, 0, 0, 0, 0
    )

    while True:
        request_global_position_int()
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        current_alt = msg.relative_alt / 1000.0  # Convert millimeters to meters
        if current_alt <= 0.2:  # 20 cm threshold for landing
            print("Landed successfully")
            break
        time.sleep(2)

finally:
    print("Closing connection")
    master.close()
