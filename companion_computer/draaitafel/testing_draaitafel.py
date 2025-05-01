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

# Concat the command for new position
cmd = "LD 90 DG NP GO"

# Go to set new position
Write(cmd)
time.sleep(2)
# Concat the command for new position
cmd = "LD 0 DG NP GO"

# Go to set new position
Write(cmd)