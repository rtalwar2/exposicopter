from pymavlink import mavutil

# Connect to the UDP or TCP port where Mission Planner is mirroring the MAVLink stream
# Replace 'udp:127.0.0.1:14550' with 'tcp:127.0.0.1:5760' if you're using TCP
# mavlink_connection = mavutil.mavlink_connection('udp:127.0.0.1:14550')
mavlink_connection = mavutil.mavlink_connection("udp:192.168.0.124:14550") #win ip addres when sitl in wsl
# mavlink_connection = mavutil.mavlink_connection('tcp:127.0.0.1:5763')
print("Listening for MAVLink messages...")

# Continuously read MAVLink messages
while True:
    # Wait for a MAVLink message
    msg = mavlink_connection.recv_match(type='STATUSTEXT',blocking=True)
    # msg = mavlink_connection.recv_match(blocking=True)
    print(msg)
    if msg:
        # Print the received message type and content
        # print(f"Received message: {msg.get_type()}")
        if msg.get_type() == "STATUSTEXT":
            print(msg.to_dict()["text"])