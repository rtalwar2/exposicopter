import sys
import os
import time
import serial
import csv
import threading
from datetime import datetime
import socket

def Write(cmd):
    """Send the input cmd string via TCPIP Socket"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))

    s.send(cmd.encode())
    print(datetime.now().time(), "Sent: ", cmd)

    time.sleep(TCP_CMDDELAY)  # Commands may be lost when writing too fast
    s.close()

def Query(cmd):
    """Send the input cmd string via TCPIP Socket and return the reply string"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))

    s.send(cmd.encode())
    data = s.recv(TCP_BUFFER)
    value = data.decode("utf-8")

    # Cut the last character as the device returns a null terminated string
    value = value[:-1]
    print(datetime.now().time(), "Sent: ", cmd)
    print(datetime.now().time(), "Recv: ", value)

    s.close()

    return value

# Initialize Constants
TCP_IP = "172.16.1.94"
TCP_PORT = 200
TCP_BUFFER = 128
TCP_CMDDELAY = 0.1


# Query device identification string
Query("*IDN?")

# Set DV 1 (Turntable) as active device
Write("LD 1 DV")

# Query current position
Query("RP")

# Preset the speed to 2.0 °/s
Write("LD 5 SF")

# Concat the command for new position
cmd = "LD 0 DG NP GO"

# Go to set new position
Write(cmd)

# Wait until the device starts moving (BU returns 1)
while True:
    bu = Query("BU")
    if bu == "1":
        break

# Wait until the device finished moving (BU returns 0)
while True:
    bu = Query("BU")
    Query("RP")  # Also display current position
    if bu == "0":
        break
# Preset the speed to 2.0 °/s
Write("LD 2 SF")
#############################################""
# Define the folder where CSV files should be saved
raw_data_folder = "draaitafel-raw-data"

# Ensure the folder exists
os.makedirs(raw_data_folder, exist_ok=True)


# Add the parent directory (where "Drone" resides) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Setup serial connection to Adafruit Feather
ser = serial.Serial('COM14', 9600, timeout=1)

# Generate CSV filename using current datetime + custom parameter
custom_param = "a3600mhz-15dbm" + "-raw"
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Generate CSV filename with the correct folder path
csv_filename = os.path.join(raw_data_folder, f"{timestamp}_{custom_param}.csv")

test_duration = 6*60+1  # 2 minutes


# Open CSV file
with open(csv_filename, mode="w", newline="") as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(["Elapsed Time (s)", "Value"])  # Updated header

    input("press enter to start")
    
    # Concat the command for new position
    cmd = "LD 360 DG NP GO"

    # Go to set new position
    Write(cmd)
    start_time = time.time()  # Capture start time
    reverse=False
    while time.time() - start_time < test_duration:
        if time.time() - start_time >=180  and reverse==False :
            reverse=True
            # Concat the command for new position
            cmd = "LD 0 DG NP GO"

            # Go to set new position
            Write(cmd)
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
