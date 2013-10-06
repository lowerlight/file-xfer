#!/usr/bin/python3
# server.py

import socket
from ftplib import FTP


# Create a socket object
server_socket = socket.socket()

# Get host name
server_host = socket.gethostname()
print (('Host is', server_host))
print (('with IP addr', socket.gethostbyname(server_host)))

# Reserve the port
server_port = 12345

# Bind the host on the port
server_socket.bind((server_host, server_port))

# this is a unicode string
str_to_be_sent = 'Thank you for connecting'

# Dictionary of available FTP commands
# ftp_cmd = {
#             'dir':'dir',
#             }

server_socket.listen(5)
to_continue = True

while(to_continue):
    print ('Waiting for client to connect')
    conn, addr = server_socket.accept()
    print (('Got connection from', addr))

    conn.send(str_to_be_sent.encode())    # encode() is used to encode str_to_be_sent as byte string
    conn.close()

    # Comment this out if want to let the server forever on
    if input("End program? Type y for yes \n") == 'y':
        to_continue = False