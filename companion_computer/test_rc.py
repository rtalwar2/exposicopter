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

# Setup serial connection to Adafruit Feather
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# Generate CSV filename using current datetime + custom parameter
# custom_param = "sweep-rpm-telem-on-rc-on"
custom_param = "rc-on6"
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_filename = f"{timestamp}_{custom_param}.csv"

test_duration=30

# Function to run motor spin in a separate thread
def run_motor_spin():
    # drone.test_motor_spin_all_increasing(1020, 1300, 1, total_duration=test_duration)
    # drone.test_motor_spin_all(2000,test_duration)
    # max is 2000

    pass
# Start motor spin in a separate thread
motor_thread = threading.Thread(target=run_motor_spin)

# Open CSV file
with open(csv_filename, mode="w", newline="") as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(["Timestamp", "Average", "Min", "Max", "Median"])  # Write header row

    # Start measurements
    motor_thread.start()
    start_time = time.time()
    while time.time() - start_time < test_duration:
        line = ser.readline().decode('utf-8').rstrip()  # Read and decode
        if line:
            try:
                # Convert sensor data to numbers
                values = list(map(float, line.split(",")))
                avg = values[0]
                min_val = values[1]
                max_val = values[2]
                median_val = values[3]

                # Print & Save to CSV
                print(f"Avg: {avg}, Min: {min_val}, Max: {max_val}, Median: {median_val}")
                csv_writer.writerow([datetime.now().strftime("%H:%M:%S"), avg, min_val, max_val, median_val])

            except ValueError:
                print(f"Invalid data received: {line}")

# Ensure the motor thread finishes
motor_thread.join()

# Ensure the drone stops after measurements
drone.sleep()
print(f"Data saved to {csv_filename}")
