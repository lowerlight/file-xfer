#!/usr/bin/python3
# server.py

# import sys
import socket

# Create a socket object
server_socket = socket.socket()

# Get host name
server_host = socket.gethostname()

# Reserve the port
server_port = 12345

# Bind the host on the port
server_socket.bind((server_host, server_port))

# this is a unicode string
str_to_be_sent = 'Thank you for connecting'

server_socket.listen(5)
to_continue = True
while(to_continue):
    conn, addr = server_socket.accept()
    print (('Got connection from', addr))

    conn.send(str_to_be_sent.encode())    # encode() is used to encode str_to_be_sent as byte string
    conn.close()

    if input("End program? Type y for yes \n") == 'y':
        to_continue = False