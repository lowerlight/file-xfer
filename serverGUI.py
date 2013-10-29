#!/usr/bin/python3
# serverGUI.py

VERSION = "0.0 RELEASE"
import os, tkinter, threading
from tkinter import ttk, constants

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer

class ServerApp(tkinter.Frame):
    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.grid(row=0, column=0)

        self.initialise()

        # Main Frame
        master.geometry("480x120")
        master.minsize(240,120)
        master.title("FTP Server")

        self.create_server_control_frame()
        self.create_start_button()
        self.create_stop_button()
        self.create_state_frame()

        self.authorizer = DummyAuthorizer()

        self.handler = FTPHandler
        self.handler.authorizer = self.authorizer
        self.handler.banner = "FTP Server ver %s is ready" % VERSION #does this work in Python3?

        self.address = ("127.0.0.1", int(21))

        self.server = ThreadedFTPServer(self.address, self.handler)
        # change this to self.server = MultiprocessFTPServer(self.address, self.handler)
        # to allow spawning a new process when another client connects
        self.server.max_cons = 256
        self.server.max_cons_per_ip = 5

    def create_server_control_frame(self):
        # Server Control Frame
        self.start_stop_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.start_stop_frame.grid(row=0, column=0, columnspan=4)
        ttk.Label(self.start_stop_frame, text="Server Control ").grid(row=0, column=0)

    def create_start_button(self):
        self.start_button = ttk.Button(self.start_stop_frame, text="Start", command=self.start_server)
        self.start_button.grid(row=0, column=2)

    def create_stop_button(self):
        self.stop_button = ttk.Button(self.start_stop_frame, text="Stop", state=['disabled'],
                        command=self.stop_server)
        self.stop_button.grid(row=0, column=3)

    def create_state_frame(self):
        # State Frame
        state_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        state_frame.grid(row=1, column=0, columnspan=3)
        ttk.Label(state_frame, text="Server State").grid(row=1, column=0)

        state_value = ttk.Label(state_frame, textvariable=self.current_state, foreground='blue')
        state_value.grid(row=1, column=2)

    def initialise(self):
        # Initial values
        self.username = tkinter.StringVar()
        self.username.set("user")

        self.password = tkinter.StringVar()
        self.password.set("passwd")

        self.root_dir = tkinter.StringVar()
        self.root_dir.set(os.getcwd() + os.sep)

        self.current_state = tkinter.StringVar()
        self.current_state.set("not running")

        self.listen_ip = tkinter.StringVar()
        self.listen_ip.set("127.0.0.1")

        self.listen_port = tkinter.StringVar()
        self.listen_port.set("21")

    def start_server(self):
        self.authorizer.add_user(self.username.get(), self.password.get(), str(self.root_dir.get()),
            'elradfmw')
        self.address = (self.listen_ip.get(), int(self.listen_port.get()))
        self.start_button.state(['disabled'])
        self.stop_button.state(['!disabled'])
        self.current_state.set("RUNNING")
        self.server.serve_forever() # WARNING: Must find a way to prevent this from blocking!

    def stop_server(self):
        self.server.close_all()
        self.authorizer.remove_user(self.username.get())
        self.start_button.state(['!disabled'])
        self.stop_button.state(['disabled'])
        self.current_state.set("NOT RUNNING")

if __name__ == '__main__':
    tk = tkinter.Tk()
    app = ServerApp(master=tk)
    app.mainloop()
    try:
        app.server.close_all()
    except:
        pass
