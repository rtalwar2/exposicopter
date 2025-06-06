#! /bin/bash
#make sure to execute this as non root or else sim_vehice.py will not be found
# argument of script is the ip address you want to make this simulation available at
# localhost or wsl local ip address in case of running in wsl
cd
cd ./ardupilot/ArduCopter/
. ~/.profile
sim_vehicle.py --out udp:$1:14560 --out udp:$1:14550