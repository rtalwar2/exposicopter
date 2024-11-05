import asyncio
import random
from mavsdk import System
import socket
async def run():

    drone = System()
    print(drone)
    
    await drone.connect("tcp://192.168.129.7:5763") #ip adres van ipconfig wireless lan adapter wifi

    # Wait for drone to connect
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connected!")
            break

    # # Wait for GPS fix
    # print("Waiting for GPS fix...")
    # async for health in drone.telemetry.health():
    #     print(health,flush=True)
    #     if health.is_global_position_ok and health.is_home_position_ok:
    #         print("GPS fix obtained!")
    #         break
    await drone.action.arm()
    await drone.action.takeoff()

if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(run())
    asyncio.run(run())
