#!/usr/bin/python3
# client.py

import socket

# Create socket object
client_socket = socket.socket()

# Get host name
client_host = socket.gethostname()

# Reserve the port
client_port = 12345

# Connect the host on the port
client_socket.connect((client_host, client_port))
print ("Received from server:")
print (client_socket.recv(1024).decode())
# decode() is used to decode the byte string data received as unicode string
client_socket.close()



