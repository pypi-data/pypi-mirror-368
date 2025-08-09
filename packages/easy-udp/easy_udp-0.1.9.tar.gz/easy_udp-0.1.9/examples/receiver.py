from easy_udp import UDPReceiver
import numpy as np
import time

# Create UDP receiver instance (small timeout to avoid busy-wait)
udp_receiver = UDPReceiver(host="localhost", port=12345, recv_timeout_s=0.1)

# receive data
while True:
    t = time.time()
    received_data = udp_receiver.receive()
    if received_data is not None:
        if isinstance(received_data, np.ndarray):
            received_data = received_data.reshape((1280, 720, 3))
            print("Received: img", received_data)
        elif isinstance(received_data, str):
            print("Received: str", received_data)
        elif isinstance(received_data, int):
            print("Received: int", received_data)
        else:
            print("Received: object", type(received_data), received_data)
        print("Time: ", time.time() - t)
