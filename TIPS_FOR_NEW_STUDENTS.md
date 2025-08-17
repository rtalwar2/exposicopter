# Tips for Future Students

This document contains a collection of tips, best practices, and troubleshooting advice gathered during the development of this thesis.

## 🚁 Flight Operations and Safety

Safety should always be your top priority when operating the drone.

*   **Configure Your Flight Modes Wisely**: The 3-position switch on your remote controller is perfect for quickly changing flight modes. However, it's strongly recommended that you **never** set one of the switch positions to **Manual** mode if not needed. An accidental switch flick could lead to a crash if you are not an experienced pilot.
*   **Recommended Safe Flight Modes**: For general operation and testing, the safest and most useful flight modes are:
    *   **Loiter**: Holds the drone's position, altitude, and heading using GPS. Excellent for pausing a mission or taking a moment to think.
    *   **AltHold (Altitude Hold)**: Holds the drone's altitude, but allows it to drift with the wind. Useful when GPS reception is poor.
    *   **Land** or **RTL (Return to Launch)**: Use these as a failsafe to land the drone safely or have it return to its takeoff location automatically.
*   **Use Simple Mode for Easier Piloting**: If you are an inexperienced pilot, check the "Simple Mode" box when configuring your flight modes in Mission Planner. This mode makes the drone move relative to the pilot's direction, regardless of which way the drone's "nose" is pointing, making orientation much easier.

## 🛠️ Tuning the Drone: Autotune Advice

Autotuning is a critical step for stable flight, but it must be done carefully.

*   **Tuning Roll and Pitch**: You can safely perform an autotune for the **roll** and **pitch** axes while the drone is in **Loiter** mode. The drone will hold its position while performing the necessary twitching maneuvers.
*   **⚠️ Critical Advice for Yaw Tuning**: **DO NOT** attempt to autotune the **yaw** axis in Loiter mode. This will cause the drone to spin uncontrollably and will almost certainly result in a crash. For yaw tuning, always use **AltHold** mode. This allows the drone to drift, but it will remain stable during the yaw tuning process.

## ✅ Pre-Flight Checklist

A few simple checks before every flight can save you from a catastrophic failure.

*   **Balance the Battery**: Always ensure the battery is centered on the drone's frame. An imbalanced center of gravity will lead to unstable flight as the motors work harder to compensate.
*   **Tighten the Propellers**: Before takeoff, double-check that all propellers are securely tightened. Loose props will fly away after landing.

## 💻 Simulation and Code

The easiest way to get familiar with the code and drone behavior is by using the simulator.

*   **Use Mission Planner's Built-in Simulator**: The quickest way to start a simulation is directly within Mission Planner. From the "Simulation" tab, simply select the "X" frame type for a multirotor. This launches a simulated drone that you can connect to instantly.
*   **Understanding the `Drone.py` Class**: The `Drone/Drone.py` file is a high-level abstraction layer, built on top of the Pymavlink library. Its purpose is to simplify common drone commands (like takeoff, fly to location, etc.) into easy-to-use functions.
*   **See an Example in Action**: The `companion_computer/pymavlink_hello_world.py` script is a great starting point to see how the `Drone.py` class is used to control the drone and execute a mission. However if to overwhelming you can simply start with arming and disarming the drone and slowl using more and more functions available in the class.

## 🔧 Common Troubleshooting Steps

If you run into issues, check these common problems first.

*   **Check Your Windows Firewall Rules**: A very common issue when running this setup on Windows + WSL2 is that the Windows Firewall blocks communication. If Mission Planner, MAVProxy (in WSL), or your Python backend script cannot connect to each other, **triple-check your firewall rules**. You may need to create an explicit inbound rule to allow Python or other applications to accept connections.
*   **Verify IP Addresses and Ports**: The system relies on communication between different components using IP addresses (especially for WSL). If things aren't connecting, ensure that the IP addresses in the scripts (`backend/main.py`, `automate_everything.ps1`, etc.) match the current IP address of your WSL instance.
*   **Read the ArduPilot Documentation**: The ArduPilot wiki is an incredibly valuable resource. If you have questions about flight modes, parameters, or MAVLink commands, the answer is most likely there. Also don't hesitate to ask me questions about the drone.
*   **ESC Configurator**: When wanting to update the ESC firmware and not being able to connect to the ESC's, disconnect the GPS and telemetry cable from the flight controller and also turn of the RC, these can cause interference.

## 🔩 Hardware Information

The drone platform used for this thesis is the **Holybro X500 V2 Development Kit**. You can find more details about it here:
[https://holybro.com/products/px4-development-kit-x500-v2](https://holybro.com/products/px4-development-kit-x500-v2)

Good luck