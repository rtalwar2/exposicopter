import sys
import os
import time
import serial
import csv
import threading
from datetime import datetime


# Define the folder where CSV files should be saved
raw_data_folder = "draaitafel-raw-data"

# Ensure the folder exists
os.makedirs(raw_data_folder, exist_ok=True)


# Add the parent directory (where "Drone" resides) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Setup serial connection to Adafruit Feather
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# Generate CSV filename using current datetime + custom parameter
custom_param = "3600mhz-15dbm" + "-raw"
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Generate CSV filename with the correct folder path
csv_filename = os.path.join(raw_data_folder, f"{timestamp}_{custom_param}.csv")

test_duration = 6 * 60  # 2 minutes


# Open CSV file
with open(csv_filename, mode="w", newline="") as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(["Elapsed Time (s)", "Value"])  # Updated header

    input("press eneer to start")
    start_time = time.time()  # Capture start time
    
    while time.time() - start_time < test_duration:
        line = ser.readline().decode('utf-8').rstrip()  # Read and decode
        if line:
            try:
                value = float(line)  # Convert sensor data to float
                elapsed_time = time.time() - start_time  # Get elapsed time in seconds
                formatted_time = f"{elapsed_time:.3f}"  # Include milliseconds (3 decimal places)

                # Print & Save to CSV
                print(f"Time: {formatted_time} s | Data: {value}")
                csv_writer.writerow([formatted_time, value])  # Save elapsed time instead of HH:MM:SS

            except ValueError:
                print(f"Invalid data received: {line}")


print(f"Data saved to {csv_filename}")
