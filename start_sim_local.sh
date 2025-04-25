#! /bin/bash
#make sure to execute this as non root or else sim_vehice.py will not be found

cd
cd ./ardupilot/ArduCopter/
. ~/.profile
sim_vehicle.py --out udp:$1:14560 --out udp:$1:14550