import serial
import time

# Change serial port to ttyACM0
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  

try:  
    while True: 
        line = ser.readline().decode('utf-8').rstrip()  # Read and decode
        if line:  # Only print if data is received
            print(line)
        # time.sleep(0.1)  
except KeyboardInterrupt:
    print("Program terminated!") 
    ser.close()  # Close serial port
