from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from pymavlink import mavutil
import threading
import uvicorn
import json
import csv
from datetime import datetime
from fastapi.staticfiles import StaticFiles
import sys
import os
import asyncio
# Add the parent directory (where "Drone" resides) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the Drone class from Drone/Drone.py
from Drone.Drone import Drone

app = FastAPI()

# location data model
class Location(BaseModel):
    lat: float
    lon: float

# Measurement data model
class Measurement(BaseModel):
    lat: float
    lon: float
    value: float


# Grid data model
class Grid(BaseModel):
    forward: float
    right: float

# Global variable to store the latest measurements
measurements = []
connections = []  # To store active WebSocket connections

# Create a CSV file with the current date and time
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_filename = f"measurements_{current_time}.csv"
drone=None
drone_connected = False  # Indicates if the drone is connected

# Function to notify all connected clients
async def notify_clients(data):
    global connections
    for connection in connections:
        try:
            await connection.send_json(data)
        except WebSocketDisconnect:
            connections.remove(connection)


# Function to listen to MAVLink messages and update the measurements list
# executed in a separate thread
def listen_for_mavlink():
    global measurements
    global drone
    global drone_connected
    print("waiting for heartbeat, please start proxy server")
    # connection_string = "udp:172.31.48.1:14560" #ip adress of local wsl instance, is fixed
    connection_string = 'tcp:127.0.0.1:5763' #ip adress of local wsl instance, is fixed
    drone = Drone(connection_string,source_system=1,source_component=3)
    print("Listening for MAVLink messages...")
    drone_connected=True
    while True:
        msg = drone.connection.recv_match(type='STATUSTEXT',blocking=True)
        if msg:
            text_data = msg.to_dict()["text"]
            print(text_data)
            # Check if the text data matches the expected format
            if msg.get_srcComponent()==2 and "V" in text_data:
            # if "V" in text_data:
                try:
                    print(text_data)
                    json_data = json.loads(text_data)
                    print(json_data.keys())
                    # Add the new measurement to the list
                    measurement = Measurement(lat=json_data['lat'], lon=json_data["lon"], value=json_data["V"])
                    measurements.append(measurement)

                    # write to csv
                    with open(csv_filename, mode='a', newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow([json_data['lat'], json_data["lon"], json_data["V"]])

                    # Notify connected WebSocket clients
                    asyncio.run(notify_clients(measurement.dict()))
                except ValueError:
                    print("Failed to parse measurement data")
                    print(text_data)


@app.post("/inspect")
def inspect_location(loc:Location):
    drone.send_message(f"lat:{loc.lat} lon:{loc.lon}")

@app.post("/grid")
def send_grid(gr:Grid):
    drone.send_message(f"fw:{gr.forward} rt:{gr.right}")

@app.get("/sensor_data", response_model=list[Measurement])
def read_sensor_data() -> list[Measurement]:
    return measurements

# Endpoint to check drone connection status
@app.get("/connection_status")
def connection_status():
    global drone_connected
    return {"drone_connected": drone_connected}


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        connections.remove(websocket)


app.mount("/", StaticFiles(directory="backend\\frontend", html=True), name="static")


def create_csv():
    # Initialize the CSV file with headers
    with open(csv_filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Latitude", "Longitude", "Value"])



if __name__ == '__main__':
    create_csv()
    # Start the MAVLink listener in a separate thread
    thread = threading.Thread(target=listen_for_mavlink, daemon=True)
    thread.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)