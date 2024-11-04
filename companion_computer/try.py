import asyncio
import random
from mavsdk import System
import socket
async def run():
    # Init the drone
    #UART 4
    print("System server b4")
    drone = System()
    print("System server done")
    await drone.connect(system_address="tcp://192.168.129.7:5763")

    drone.telemetry.status_text() #Subscribe to ‘status text’ updates.
    await asyncio.sleep(1)
    status_text_task = asyncio.ensure_future(print_status_text(drone))

    print("Pi4B Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to drone!")
            break

    info = await drone.info.get_version()
    print(info)

    # Start the tasks
    await drone.telemetry.set_rate_battery(1) #1hz
    await asyncio.sleep(1)
    telem_battery = asyncio.ensure_future(print_battery(drone))

    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.takeoff()

    print("-- Landing")
    await drone.action.land()

    await asyncio.sleep(3)
    status_text_task.cancel()
    await asyncio.sleep(3)
    telem_battery.cancel()

async def print_status_text(drone):
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        print("print_status_text CancelledError")
        return

async def print_battery(drone):
    try:
        async for battery in drone.telemetry.battery():
            print(f"Battery: {battery.remaining_percent}")
            print(f"Battery_v: {battery.voltage_v}")
    except asyncio.CancelledError:
        print("print_battery CancelledError")
        return

if __name__ == "__main__":
    asyncio.run(run())