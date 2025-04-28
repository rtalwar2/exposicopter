#!/bin/bash
# Make sure to execute this as non-root or else sim_vehicle.py will not be found
# Argument is the local WSL address, e.g., 172.31.48.1

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Error: Missing IP address argument."
  echo "Usage: $0 <WSL_IP_Address>"
  echo "Example: bash $0 172.31.48.1"
  exit 1
fi

cd
. ~/.profile
mavproxy.py --master=/dev/ttyUSB0,57600 --out udp:$1:14560 --out udp:$1:14550