#!/usr/bin/python3
# client.py

import socket
from ftplib import FTP


# Create a socket object
client_socket = socket.socket()

# Get host name
client_host = socket.gethostname()
print (('Client is', client_host))
print (('with IP addr', socket.gethostbyname(client_host)))

# Reserve the port
client_port = 12345

# Display ftp prompt
print ('Type y to try connecting to the server')
while input("ftp>") != 'y':
    pass

# Match the ftp command with what to do here


# E.g. Connect to the host on the port
client_socket.connect((client_host, client_port))

print ("Received from server:")
print (client_socket.recv(1024).decode())
# decode() is used to decode the byte string data received as unicode string

client_socket.close()



