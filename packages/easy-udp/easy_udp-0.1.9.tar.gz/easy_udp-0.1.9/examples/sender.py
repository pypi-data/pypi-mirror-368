from easy_udp import UDPSender
import numpy as np
import time

# Create UDP sender instance
udp_sender = UDPSender(host="localhost", port=12345)

# Sending data
print("Sending: 123")
udp_sender.send(123)

print("Sending: Hello, World!")
udp_sender.send("Hello, World!")

img = np.random.randint(0, 255, (1280, 720, 3), dtype=np.uint8)
udp_sender.send(img)

# Send arbitrary object
obj = {"msg": "hello", "numbers": [1, 2, 3]}
print("Sending: object", obj)
udp_sender.send(obj)
