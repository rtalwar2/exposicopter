import collections.abc

collections.MutableMapping = collections.abc.MutableMapping
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import random

# Connect to the Pixhawk on the companion computer (e.g., via UART or USB)
# Adjust connection string as needed
connection_string = 'tcp://192.168.129.7:5763'
print("Connecting to vehicle on:", connection_string)
vehicle = connect(connection_string, wait_ready=True, baud=57600)

def wait_for_gps_fix(vehicle):
    """
    Wait for the vehicle to have a valid GPS fix.
    """
    print("Waiting for GPS fix...")
    while not vehicle.is_armable:
        print("Waiting for vehicle to become armable...")
        time.sleep(1)
    print("GPS fix obtained!")

def arm_and_takeoff(target_altitude):
    """
    Arms the vehicle and makes it take off to target_altitude.
    """
    print("-- Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Wait for the vehicle to be armed
    while not vehicle.armed:
        print("Waiting for arming...")
        time.sleep(1)

    print("-- Taking off")
    vehicle.simple_takeoff(target_altitude)

    # Wait until the vehicle reaches a safe height
    while True:
        print(f"Altitude: {vehicle.location.global_relative_frame.alt}")
        if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

def fly_to_location(lat, lon, alt):
    """
    Command the vehicle to fly to a specific location (lat, lon, alt).
    """
    location = LocationGlobalRelative(lat, lon, alt)
    print(f"Flying to {lat}, {lon} at altitude {alt} meters")
    vehicle.simple_goto(location)

    # Wait until the vehicle reaches the location
    time.sleep(10)  # Adjust as needed for precision

def send_random_data():
    """
    Send a random number to the ground control station via telemetry.
    """
    random_number = random.randint(1, 100)
    print(f"Sending random data: {random_number}")
    vehicle.message_factory.command_long_encode(
        0, 0,           # target system, target component
        183,            # MAV_CMD_USER_1
        0,              # Confirmation
        random_number,  # Param 1, send data
        0, 0, 0, 0, 0, 0  # Params 2-7 not used
    )
    # Log for GCS; DroneKit doesn't have a built-in method to directly send custom MAVLink messages

# Main execution
try:
    wait_for_gps_fix(vehicle)
    arm_and_takeoff(10)  # Adjust altitude as needed

    # Replace with actual waypoints
    mission_waypoints = [
        (50.823784, 3.240393, 10),  # Example coordinates
        (50.823800, 3.240500, 10),
        (50.823820, 3.240600, 10),
        (50.823840, 3.240700, 10)
    ]

    for waypoint in mission_waypoints:
        fly_to_location(*waypoint)
        print("-- Hovering at point")
        time.sleep(5)  # Simulate hover

        # Send random data to the ground control station
        send_random_data()

    print("-- Returning to launch")
    vehicle.mode = VehicleMode("RTL")

    # Wait for vehicle to land
    while vehicle.mode.name == "RTL":
        print("Returning home...")
        time.sleep(2)

finally:
    print("Closing vehicle connection")
    vehicle.close()
