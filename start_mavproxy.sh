#! /bin/bash
#make sure to execute this as non root or else sim_vehice.py will not be found
#argument is local wsl address, in my case 172.31.48.1
cd
. ~/.profile
mavproxy.py --master=/dev/ttyUSB0,57600 --out udp:$1:14560 --out udp:$1:14550
