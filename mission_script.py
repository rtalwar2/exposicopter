import asyncio
import random
from mavsdk import System
import socket
async def run():

    drone = System()
    print(drone)
    
    await drone.connect("tcp://192.168.129.7:5763") #ip adres van ipconfig wireless lan adapter wifi
    # Wait for the drone to connect
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connected!")
            break

    # Wait for GPS fix
    # print("Waiting for GPS fix...")
    # async for health in drone.telemetry.health():
    #     if health.is_global_position_ok and health.is_home_position_ok:
    #         print("GPS fix obtained!")
    #         break

    # Download mission (the rectangle's 4 coordinates) from Pixhawk
    # mission_items = await get_mission_items(drone)

    # if not mission_items:
    #     print("No mission received!")
    #     return

    # Start manual control of the mission
    # print("-- Arming")
    # await drone.action.arm()

    # print("-- Taking off")
    # await drone.action.takeoff()
    # await asyncio.sleep(5)

    # Fly according to the mission waypoints received from Pixhawk
    # for mission_item in mission_items:
    #     await fly_to(drone, mission_item.latitude_deg, mission_item.longitude_deg, mission_item.relative_altitude_m)
    #     print("-- Hovering at point")
    #     await asyncio.sleep(5)
    print("starting mission")
    await drone.mission.start_mission()
    await asyncio.sleep(50)

        # Send random data to GCS (Mission Planner) via Pixhawk and Telemetry Radio
        # await send_random_data_to_gcs(drone)

    # Return to launch
    print("-- Returning home")
    await drone.action.return_to_launch()

async def get_mission_items(drone):
    """
    Fetch the mission items (4 points) from the Pixhawk, which were uploaded via Mission Planner.
    """
    mission_items = []
    print("Fetching mission items from Pixhawk...")
    mission_plan = drone.mission.download_mission()
    for item in mission_plan.mission_items:
        mission_items.append(item)
    print(f"Received {len(mission_items)} mission items.")
    return mission_items

async def fly_to(drone, lat, lon, alt):
    """
    Manually fly to the specific coordinates (lat, lon, alt) instead of using Pixhawk's auto mission execution.
    """
    print(f"Flying to {lat}, {lon} at altitude {alt} meters")
    await drone.action.goto_location(lat, lon, alt, 0)
    await asyncio.sleep(10)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())