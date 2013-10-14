#!/usr/bin/python3
# serverGUI.py

VERSION = "0.0 RELEASE"
import os, tkinter, threading
#from tkinter import *
from tkinter import ttk, constants

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

tk = tkinter.Tk()

# Initial values
username = tkinter.StringVar()
username.set("user")

password = tkinter.StringVar()
password.set("passwd")

root_dir = tkinter.StringVar()
root_dir.set(os.getcwd() + os.sep)

current_state = tkinter.StringVar()
current_state.set("not running")

listen_ip = tkinter.StringVar()
listen_ip.set("127.0.0.1")

listen_port = tkinter.StringVar()
listen_port.set("21")



# Callback handlers

# temp global declarator
authorizer = None
handler = None
server = None

# class Action:
def start_server():
    global authorizer   #temp
    authorizer = DummyAuthorizer()
    authorizer.add_user(username.get(), password.get(), str(root_dir.get()), 'elradfmw')

    global handler #temp
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "FTP Server ver %s is ready" % VERSION #does this work in Python3?

    address = (listen_ip.get(), int(listen_port.get()))

    global server  #temp
    server = FTPServer(address, handler)
    server.max_cons = 256
    server.max_cons_per_ip = 5

    start_button.state(['disabled'])
    stop_button.state(['!disabled'])
    current_state.set("RUNNING")

    threading.Thread(target=server.serve_forever).start()

def stop_server():
    global authorizer   #temp
    global handler #temp
    global server  #temp

    server.close_all()

    del authorizer   #temp
    del handler #temp
    del server  #temp

    start_button.state(['!disabled'])
    stop_button.state(['disabled'])
    current_state.set("NOT RUNNING")

# Main Frame

tk.geometry("480x120")
tk.minsize(240,120)
tk.title("FTP Server")

# Server Control Frame
start_stop_frame = ttk.Frame(tk, relief=constants.SOLID, borderwidth=1)
start_stop_frame.grid(row=0, column=0, columnspan=4)
ttk.Label(start_stop_frame, text="Server Control ").grid(row=0, column=0)

start_button = ttk.Button(start_stop_frame, text="Start", command=start_server)
start_button.grid(row=0, column=2)

stop_button = ttk.Button(start_stop_frame, text="Stop", state=['disabled'], command=stop_server)
stop_button.grid(row=0, column=3)

# State Frame
state_frame = ttk.Frame(tk, relief=constants.SOLID, borderwidth=1)
state_frame.grid(row=1, column=0, columnspan=3)
ttk.Label(state_frame, text="Server State").grid(row=1, column=0)

state_value = ttk.Label(state_frame, textvariable=current_state, foreground='blue')
state_value.grid(row=1, column=2)

# Main
tk.mainloop()
try:
    server.close_all()
except:
    pass

# if __name__ == '__main__':
#     main()