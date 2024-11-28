#! /bin/bash

cd
cd ./ardupilot/ArduCopter/
. ~/.profile
sim_vehicle.py --out udp:$1:14560 --out udp:$1:14550