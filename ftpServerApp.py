#!/usr/bin/python3
# ftpServerApp.py

"""
Project : Network Programming Assignment Question
Filename : ftpServerApp.py
Author : Jeffrey Nursalim
Student No: TP031319
Module Code & Title: CE00731-M Network Systems and Technologies
Due Date : 09 December 2013

Tested with ftplib changeset 38db4d0726bd found at
http://hg.python.org/cpython/file/38db4d0726bd/Lib/ftplib.py
and pyftpdlib ver 1.3.0 released on 2013-11-07 found at
http://pyftpdlib.googlecode.com/files/pyftpdlib-1.3.0.tar.gz

The MIT License (MIT)

Copyright (c) 2014 Jeffrey Nursalim

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

VERSION = "1.0 RELEASE"

LOWEST_PORT_NO = 1025
HIGHEST_PORT_NO = 65533

import os, tkinter, threading, sys, re, socket
from functools import partial
from tkinter import ttk, constants, filedialog
import tkinter.messagebox as mbox

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer

from ftpGUI import RootTree, StdoutRedirector

class FTPServerApp(tkinter.Frame):
    root_dir = dict()
    root_dir_tree = dict()
    dir_tree_frame = dict()

    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.grid(row=0, column=0)

        # Main Frame
        master.minsize(480,640)
        self.local_ip_addr = socket.gethostbyname(socket.getfqdn())
        self.local_port = int(LOWEST_PORT_NO)
        master.title("FTP Server by TP031319 at %s" % (self.local_ip_addr,))

        self.authorizer = DummyAuthorizer()
        self.initialise()

        self.create_server_control_frame(rw=0, cl=0)
        self.create_input_frame(rw=0, cl=3)
        self.create_state_frame(rw=1, cl=0)

        self.create_dir_frame(rw=4, cl=0)
        self.create_dir_tree_frame(rw=7, cl=0, tit="Local")

        self.create_browse_button(rw=5, cl=4)
        self.create_share_button(rw=5, cl=5)

        self.create_stderr_frame(rw=12, cl=0)

        self.handler = FTPHandler
        self.handler.authorizer = self.authorizer
        self.handler.banner = "FTP Server ver %s is ready" % VERSION #does this work in Python3?

    def create_server_control_frame(self, rw, cl):
        # Server Control Frame
        self.server_control_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.server_control_frame.grid(row=rw, column=cl, columnspan=4, sticky=constants.W,
            pady=4, padx=5)
        ttk.Label(self.server_control_frame, text="Server Control ").grid(row=rw, column=cl)

        self.start_button = ttk.Button(self.server_control_frame, text="Start",
            command=self.start_server)
        self.start_button.grid(row=rw, column=cl+1)

        self.stop_button = ttk.Button(self.server_control_frame, text="Stop", state=['disabled'],
                        command=self.stop_server)
        self.stop_button.grid(row=rw, column=cl+2)

    def create_state_frame(self, rw, cl):
        # State Frame
        state_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        state_frame.grid(row=rw, column=cl, columnspan=3, sticky=constants.W, pady=4, padx=5)
        ttk.Label(state_frame, text="Server State").grid(row=rw, column=cl)

        state_value = ttk.Label(state_frame, textvariable=self.current_state, foreground='blue')
        state_value.grid(row=rw, column=cl+1)

    def create_input_frame(self, rw, cl):
        self.input_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.input_frame.grid(row=rw, column=cl, columnspan=3, sticky=constants.W, pady=4, padx=5)

        port_input_label = ttk.Label(self.input_frame,
            text="Server Port ({0}~{1})".format(LOWEST_PORT_NO, HIGHEST_PORT_NO))
        port_input_label.grid(row=rw, column=cl+1, sticky=constants.W)
        self.listen_port_input = ttk.Entry(self.input_frame, width=8, textvariable=self.listen_port)
        self.listen_port_input.grid(row=rw+1, column=cl+1)

    def create_dir_frame(self, rw, cl):
        self.dir_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.dir_frame.grid(row=rw, column=cl, columnspan=3, sticky=constants.W, pady=4, padx=5)
        ttk.Label(self.dir_frame, text="Shared Directory").grid(row=rw, column=cl,
            sticky=constants.W)

        self.root_dir_input = ttk.Entry(self.dir_frame, width=64,
            textvariable=self.root_dir['Local'])
        self.root_dir_input.grid(row=rw+1, column=cl)

    def create_browse_button(self, rw, cl):
        self.browse_button = ttk.Button(self.dir_frame, text="Browse",
            command=partial(self.select_dir, self.root_dir_tree['Local']))
        self.browse_button.grid(row=rw, column=cl)

    def create_share_button(self, rw, cl):
        self.share_button = ttk.Button(self.dir_frame, text="Share",
            command=partial(self.share_dir, self.root_dir_tree['Local']))
        self.share_button.grid(row=rw, column=cl)

    def create_dir_tree_frame(self, rw, cl, tit):
        self.dir_tree_frame[tit] = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.root_dir_tree[tit] = RootTree(self, columns=('fullpath','type','size'),
            displaycolumns='size', root_dir=self.root_dir[tit],
            conn=self.ftp_conn if tit=='Remote' else None)

        self.root_dir_tree[tit].heading('#0', text='Directory', anchor=constants.W)
        self.root_dir_tree[tit].heading('size', text='Size', anchor=constants.W)
        self.root_dir_tree[tit].column('#0', stretch=0, minwidth=200, width=440)
        self.root_dir_tree[tit].column('size', stretch=1, minwidth=40, width=80)

        self.dir_tree_frame[tit].grid(row=rw, column=cl, sticky=constants.W, pady=4, padx=5)
        ttk.Label(self.dir_tree_frame[tit], text=tit).grid(row=rw, column=cl, sticky=constants.W)
        self.root_dir_tree[tit].grid(in_=self.dir_tree_frame[tit], row=rw+1, column=cl,
            sticky=constants.NSEW)

        yScrollBar = ttk.Scrollbar(self.dir_tree_frame[tit], orient=constants.VERTICAL,
            command=self.root_dir_tree[tit].yview)
        xScrollBar = ttk.Scrollbar(self.dir_tree_frame[tit], orient=constants.HORIZONTAL,
            command=self.root_dir_tree[tit].xview)
        self.root_dir_tree[tit]['yscroll'] = yScrollBar.set
        self.root_dir_tree[tit]['xscroll'] = xScrollBar.set

        yScrollBar.grid(row=rw, column=cl+2, rowspan=3, sticky=constants.NS)
        xScrollBar.grid(row=rw+3, column=cl, rowspan=1, sticky=constants.EW)
        # set frame resizing priorities
        self.dir_tree_frame[tit].rowconfigure(0, weight=1)
        self.dir_tree_frame[tit].columnconfigure(0, weight=1)

    def create_stderr_frame(self, rw, cl):
        self.stderr_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.stderr_frame.grid(row=rw, column=cl)

        self.old_stderr = sys.stderr

        self.err = tkinter.Text(self, width=64, height=12, wrap='none')
        self.err.grid(row=rw+1, column=cl, pady=4, padx=5)
        sys.stderr = StdoutRedirector(self.err)

    def initialise(self):
        # Initial values
        self.username = tkinter.StringVar()
        self.username.set("user")

        self.password = tkinter.StringVar()
        self.password.set("passwd")

        self.listen_ip = tkinter.StringVar()
        self.listen_ip.set(self.local_ip_addr)

        self.listen_port = tkinter.StringVar()
        self.listen_port.set(self.local_port)

        self.root_dir['Local'] = tkinter.StringVar()
        self.root_dir['Local'].set(os.getcwd() + os.sep)

        self.current_state = tkinter.StringVar()
        self.current_state.set("NOT RUNNING")

        self.root_dir['Remote'] = tkinter.StringVar()
        self.root_dir['Remote'].set(os.sep)

        # This can be set up only once and saved in a database
        self.authorizer.add_user(self.username.get(), self.password.get(),
            self.root_dir['Local'].get(), 'elradfmw')

    def start_server(self):
        port_no = 0
        msg = "Please type a port number between 1025 and 65533 inclusive."
        try:
            port_no = int(self.listen_port.get())

            if port_no < LOWEST_PORT_NO or port_no > HIGHEST_PORT_NO:
                msg += " Port {0} is not valid.".format(port_no)
                raise Exception(msg)
        except:
            mbox.showinfo(message=msg)
            return

        self.address = (self.listen_ip.get(), port_no)
        self.server = ThreadedFTPServer(self.address, self.handler)
        self.server.max_cons = 256
        self.server.max_cons_per_ip = 5

        self.share_dir(self.root_dir_tree['Local'])

        self.start_button.state(['disabled'])
        self.stop_button.state(['!disabled'])
        self.share_button.state(['disabled'])
        self.current_state.set("RUNNING")

        threading.Thread(target=self.server.serve_forever).start()

    def stop_server(self):
        self.server.close_all()
        self.start_button.state(['!disabled'])
        self.stop_button.state(['disabled'])
        self.share_button.state(['!disabled'])
        self.current_state.set("NOT RUNNING")

    def select_dir(self, dir_tree_view):
        if isinstance(dir_tree_view, RootTree):
            children = dir_tree_view.get_children('')
            if children:
                dir_tree_view.delete(children)
            old_dir_tree_view_root_dir = dir_tree_view.root_directory.get()
            dir_tree_view.root_directory.set(filedialog.askdirectory().replace("/" , str(os.sep)))
            if not dir_tree_view.root_directory.get():
                dir_tree_view.root_directory.set(old_dir_tree_view_root_dir)

    def share_dir(self, dir_tree_view):
        if isinstance(dir_tree_view, RootTree):
            try:
                os.chdir(self.root_dir['Local'].get())
                dir_tree_view.root_directory = self.root_dir['Local']
                # No need to reconnect because this is only for local dir
                dir_tree_view.populate_parent()
                # Open up the directory for transferring out/receiving in files
                # For use with WindowsAuthorizer or UnixAuthorizer:
                # For simplicity's sake, update the homedir everytime Share button is pressed
                # self.authorizer.override_user(self.username.get(),
                # homedir=self.root_dir['Local'].get())
                # For now the workaround:
                self.authorizer.remove_user(self.username.get())
                self.authorizer.add_user(self.username.get(), self.password.get(),
                    self.root_dir['Local'].get(), 'elradfmw')
            except FileNotFoundError:
                mbox.showinfo(message="Invalid Directory!")

if __name__ == '__main__':
    root = tkinter.Tk()
    app = FTPServerApp(master=root)
    app.mainloop()
    try:
        app.server.close_all()
    except:
        pass

    sys.stderr = app.old_stderr
