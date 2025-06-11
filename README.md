# 📡 ExposiCopter: Drone-Based RF-EMF Measurement Platform

This repository contains all code, configuration files, and visualizations developed for my master's thesis on drone-based RF-EMF (radio-frequency electromagnetic field) mapping. The system integrates a quadcopter with real-time signal acquisition, flight automation, and interference mitigation strategies for robust wireless exposure measurements.

## 🖼 System Architecture

![System Architecture](system_architecture.png) 

## ⚙️ System Setup

The system consists of three main components:

1. **Raspberry Pi 4 (on the drone)**  
   - Run `companion_computer/pymavlink_hello_world.py` for real-time data acquisition and communication with the flight controller.

2. **Laptop (Ground Station)**  
   - Run the **FastAPI backend** located in `backend/` (manual startup required).
   - Use **Mission Planner** for mission control.
   - Start **MAVProxy** in WSL to forward telemetry between components.
   - Use `automate_everything.ps1` (as administrator) to:
     1. Attach the USB device to WSL.
     2. Launch MAVProxy.
     3. Start Mission Planner.

3. **Optional: Simulated Environment**  
   If you don’t have a physical drone, use `start_sim_local.sh` to start a simulated ArduPilot drone with MAVProxy locally. This allows full system testing in a virtual environment.

## 📁 Repository Structure
```bash
├── params/ # parameters of quadcopter
├── backend/ # FastAPI backend serving static frontend
│ ├── main.py # Launches backend and serves frontend
│ └── frontend/ # Contains frontend HTML/CSS/JS code
├── companion_computer/ # Code running on drone’s companion computer
│ ├── pymavlink_hello_world.py # Main script that runs on the Pi
│ ├── helper_functions.py # Utility functions
│ ├── draaitafel/ # Folder containing code for turntable experiments
│ └── drone_influence/ # Experiments on drone self-interference
├── Drone/ # Abstraction layer over pymavlink for drone control
│ └── Drone.py # Exposes high-level drone commands (used by pymavlink_hello_world and backend scripts)
├── experiment_results/ 
│ ├── draaitafel-raw-data/ # Raw data from turntable experiments
│ ├── draaitafel-processed-data/ # Cleaned/processed data from turntable
│ ├── processed-data/ # processed data from drone interference experiments
│ ├── raw-data/ # Raw data from drone interference experiments
│ └── raw-plots/ # drone interference raw data plots
├───flight_logs #contains flightlogs for some flights
├───raw-flight-data/ # raw flight data from companion computer flights
├── startup_script_hlpers # helper scripts for startup of system
│ ├── attach_usb_wsl.ps1 # script to attach usb device to WSL
│ └── start_mavproxy.sh # script to automatically start mavproxy server
├── automate_everything.ps1 # script to automate MP, mavproxy and USB startup
├── requirements.txt # requirements file
├── RF_analyse.ipynb # notebook use to analyse experiments
├── start_sim_local.sh # script to start simulated drone locally 
└── system_architecture.drawio # system architecture
```

## 🏃‍♂️ How to Run
On the Raspberry Pi, run:    
```bash
    python companion_computer/pymavlink_hello_world.py
```
On the laptop, open PowerShell as administrator and run:
```powershell
    .\automate_everything.ps1
```
to start the system, however to run a simulated veriosn of the drone use, 
```bash
    ./start_sim_local.sh [windows_local_ip]
```
to start mavproxy linked with simulated drone.

Then, start the backend manually:
```bash
    uvicorn backend.main:app --reload
```

## 🛠 Dependencies

- Python 3.11+
- requirements.txt

## 🙏 Acknowledgements

- Supervision: Kenneth, Jeroen, Lowie, and Han — thank you for the technical support and guidance.
- Sparring partner: Jonas
- Friends and family: Thanks for the moral and practical support throughout this thesis.

## Note
There are some hardcoded IP addresses and paths in the code and scripts that have to be adapted to the system
