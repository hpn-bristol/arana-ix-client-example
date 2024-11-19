import time
from ix_client import IxClient

# Create an Ix client instance
client = IxClient(url='http://ix-interface', username="dev_xapp_cg", password="35gJ3iHZAj3QuiAruK5hEg", data_logging=True)

# Initiate the Ix client connection
client.connect(relation_id="rel4f649bfaa044e472")

# Define dummy data
data = {"value_1": 51, "value_2": 93}

# Use IxClient.is_connected property to transmit data while the connection remains active
while True and client.is_connected:
    # Send the data
    client.send(data=data)

    # Update the dummy data
    data["value_1"] += 1
    data["value_2"] += 2
    time.sleep(1)