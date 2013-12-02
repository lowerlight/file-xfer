#!/usr/bin/python3
# ftpClientApp.py

"""
Project : Network Programming Assignment Question
Filename : ftpClientApp.py
Author : Jeffrey Nursalim
Student No: TP031319
Module Code & Title: CE00731-M Network Systems and Technologies
Due Date : 09 December 2013

Tested with ftplib changeset 38db4d0726bd found at
http://hg.python.org/cpython/file/38db4d0726bd/Lib/ftplib.py
and pyftpdlib ver 1.3.0 released on 2013-11-07 found at
http://pyftpdlib.googlecode.com/files/pyftpdlib-1.3.0.tar.gz
"""

VERSION = "1.0 RELEASE"
import os, tkinter, threading, sys, re
from socket import gethostbyname, getfqdn
from functools import partial
from tkinter import ttk, constants, filedialog
import pdb

import ftplib

from ftpGUI import RootTree, StdoutRedirector

class FTPClientApp(tkinter.Frame):
    root_dir = dict()
    root_dir_tree = dict()
    dir_tree_frame = dict()
    ftp_conn = ftplib.FTP()

    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.grid(row=0, column=0)

        self.initialise()

        # Main Frame
        # master.geometry("480x120")
        master.minsize(960,480)
        # self.local_ip_addr = gethostbyname(getfqdn())
        self.local_ip_addr = '127.0.0.1'    # debug
        master.title("FTP Server at %s" % self.local_ip_addr)

        self.create_control_frame(rw=0, cl=0)

        self.create_state_frame(rw=1, cl=0)
        self.create_input_frame(rw=3, cl=0)

        self.create_remote_dir_button(rw=1, cl=3)

        self.create_dir_frame(rw=4, cl=0)
        self.create_dir_tree_frame(rw=7, cl=0, tit="Local")
        self.create_push_file_button(rw=7, cl=1)

        self.create_dir_tree_frame(rw=7, cl=4, tit="Remote")
        self.create_pull_file_button(rw=7, cl=2)

        self.create_connect_button(rw=0, cl=1)
        self.create_disconnect_button(rw=0, cl=2)
        self.create_browse_button(rw=5, cl=4)
        self.create_share_button(rw=5, cl=5)

    def initialise(self):
        # Initial values
        self.username = tkinter.StringVar()
        self.username.set("user")

        self.password = tkinter.StringVar()
        self.password.set("passwd")

        self.root_dir['Local'] = tkinter.StringVar()
        self.root_dir['Local'].set(os.getcwd() + os.sep)

        self.current_state = tkinter.StringVar()
        self.current_state.set("DISCONNECTED")

        self.listen_ip = tkinter.StringVar()
        self.listen_ip.set("127.0.0.1")

        self.listen_port = tkinter.StringVar()
        self.listen_port.set("21")

        self.root_dir['Remote'] = tkinter.StringVar()
        self.root_dir['Remote'].set(os.sep)

    def create_control_frame(self, rw, cl):
        # Control Frame
        self.control_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.control_frame.grid(row=rw, column=cl, columnspan=4, sticky=constants.W, pady=4, padx=5)
        ttk.Label(self.control_frame, text="Client Control").grid(row=rw, column=cl)

    def create_connect_button(self, rw, cl):
        self.connect_button = ttk.Button(self.control_frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=rw, column=cl+1)

    def create_disconnect_button(self, rw, cl):
        self.disconnect_button = ttk.Button(self.control_frame, text="Disconnect",
            state=['disabled'], command=partial(self.disconnect, self.root_dir_tree['Remote']))
        self.disconnect_button.grid(row=rw, column=cl+2)

    def create_input_frame(self, rw, cl):
        self.input_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.input_frame.grid(row=rw, column=cl, columnspan=3, sticky=constants.W, pady=4, padx=5)

        # ttk.Label(self.input_frame, text="User Name").grid(row=2, column=0)
        # self.username_input = ttk.Entry(self.input_frame, textvariable=self.username)
        # self.username_input.grid(row=rw, column=cl)

        # ttk.Label(self.input_frame, text="Password").grid(row=2, column=1)
        # self.password_input = ttk.Entry(self.input_frame, textvariable=self.password)
        # self.password_input.grid(row=rw, column=cl+1)

        ttk.Label(self.input_frame, text="Server Address").grid(row=rw, column=cl,
            sticky=constants.W)
        self.listen_ip_input = ttk.Entry(self.input_frame, textvariable=self.listen_ip)
        self.listen_ip_input.grid(row=rw+1, column=cl)

        ttk.Label(self.input_frame, text="Server Port").grid(row=rw, column=cl+1,
            sticky=constants.W)
        self.listen_port_input = ttk.Entry(self.input_frame, textvariable=self.listen_port)
        self.listen_port_input.grid(row=rw+1, column=cl+1)

    def create_state_frame(self, rw, cl):
        # State Frame
        state_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        state_frame.grid(row=rw, column=cl, columnspan=3, sticky=constants.W, pady=4, padx=5)
        ttk.Label(state_frame, text="FTP Connection State").grid(row=rw, column=cl)

        state_value = ttk.Label(state_frame, textvariable=self.current_state, foreground='blue')
        state_value.grid(row=rw, column=cl+1)

    def create_browse_button(self, rw, cl):
        self.browse_button = ttk.Button(self.dir_frame, text="Browse",
            command=partial(self.select_dir, self.root_dir_tree['Local']))
        self.browse_button.grid(row=rw, column=cl)

    def create_share_button(self, rw, cl):
        self.share_button = ttk.Button(self.dir_frame, text="Share",
            command=partial(self.share_dir, self.root_dir_tree['Local']))
        self.share_button.grid(row=rw, column=cl)

    def create_dir_frame(self, rw, cl):
        self.dir_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.dir_frame.grid(row=rw, column=cl, columnspan=3, sticky=constants.W, pady=4, padx=5)
        ttk.Label(self.dir_frame, text="Local Directory").grid(row=rw, column=cl,
            sticky=constants.W)

        # TODO: Rename this to Local root dir later.
        # Now still cannot imagine how to get the remote root directory and display the tree
        self.root_dir_input = ttk.Entry(self.dir_frame, width=64,
            textvariable=self.root_dir['Local'])
        self.root_dir_input.grid(row=rw+1, column=cl)

    def create_push_file_button(self, rw, cl):
        self.push_file_button = ttk.Button(self, text="Push >>",
            command=self.push_file)
        self.push_file_button.grid(row=rw, column=cl)

    def create_pull_file_button(self, rw, cl):
        self.pull_file_button = ttk.Button(self, text="Pull <<",
            command=self.pull_file)
        self.pull_file_button.grid(row=rw, column=cl)

    def list_remote_dir(self):
        assert isinstance(self.root_dir_tree['Remote'], RootTree)
        self.reconnect()
        self.root_dir_tree['Remote'].populate_parent()

    def connect(self):
        user = self.username.get()
        pswd = self.password.get()
        host = self.listen_ip.get()
        port = int(self.listen_port.get())

        try:
            self.ftp_conn = ftplib.FTP(user=user, passwd=pswd)
            print("h1")
            self.ftp_conn.connect(host=host, port=port)
            print((host, port))
            print("h2")
            self.ftp_conn.login(user, pswd)
            print("h3")
        except:
            print("Login failed, check username, password, IP and port.")
            return

        self.root_dir_tree['Remote'].root_directory.set(str(os.sep))
        self.list_remote_dir()

        self.connect_button.state(['disabled'])
        self.disconnect_button.state(['!disabled'])
        self.current_state.set("CONNECTED!")

    def disconnect(self, dir_tree_view):
        user = self.username.get()
        pswd = self.password.get()
        host = self.listen_ip.get()
        port = int(self.listen_port.get())

        try:
             self.ftp_conn.quit()
        except:
            print("Already disconnected")
        finally:
            self.connect_button.state(['!disabled'])
            self.disconnect_button.state(['disabled'])
            self.current_state.set("DISCONNECTED")

            if isinstance(dir_tree_view, RootTree):
                children = dir_tree_view.get_children('')
                if children:
                    dir_tree_view.delete(children)

    def reconnect(self):
        self.user = self.username.get()
        self.pswd = self.password.get()
        self.host = self.listen_ip.get()
        self.port = int(self.listen_port.get())

        print(self.root_dir_tree['Remote'].ftp_conn.sock)   # TO ANSWER: why the sock go missing?!
        if not self.root_dir_tree['Remote'].ftp_conn.sock:
            self.root_dir_tree['Remote'].ftp_conn.connect(host=self.host, port=self.port)
            print("Reconnected!")
            self.root_dir_tree['Remote'].ftp_conn.login(self.user, self.pswd)
            print("Reloggedin!")

    def create_remote_dir_button(self, rw, cl):
        self.remote_dir_button = ttk.Button(self, text="Remote Dir",
            command=self.list_remote_dir)
        self.remote_dir_button.grid(row=rw, column=cl)

    def share_dir(self, dir_tree_view):
        if isinstance(dir_tree_view, RootTree):
            # No need to reconnect because this is only for local dir
            dir_tree_view.populate_parent()

    def upload_file(self, filename, outfile=None):
        if not outfile:
            outfile = sys.stdout
        self.reconnect()
        if re.search('\.txt$', filename):
            self.ftp_conn.storlines("STOR " + filename, open(filename),
                callback=lambda : print('.'))
        else:
            self.ftp_conn.storbinary("STOR " + filename, open(filename, "rb"), 1024,
                lambda : print('.'))

    def download_file(self, filename, outfile=None):
        if not outfile:
            outfile = sys.stdout
        else:
            # TODO: Check if file already exists and append number?/alert user?
            pass

        print(filename)
        self.reconnect()
        if re.search('\.txt$', filename):
            outfile = open(filename, 'w')
            self.ftp_conn.retrlines("RETR " + filename, lambda s, w=outfile.write: w(s+"\r\n"))
        else:
            outfile = open(filename, 'wb')
            self.ftp_conn.retrbinary("RETR " + filename, outfile.write)
        outfile.close()

    def push_file(self):
        files = self.root_dir_tree['Local'].selection()
        for fileinfo in files:
            print(self.root_dir_tree['Local'].item(fileinfo))
            filename = self.root_dir_tree['Local'].item(fileinfo, 'text')
            self.upload_file(filename)

    def pull_file(self):
        files = self.root_dir_tree['Remote'].selection()
        for fileinfo in files:
            print(self.root_dir_tree['Remote'].item(fileinfo))
            filename = self.root_dir_tree['Remote'].item(fileinfo, 'text')
            self.download_file(filename, outfile="out_{0}".format(filename))

    def create_dir_tree_frame(self, rw, cl, tit):
        self.dir_tree_frame[tit] = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.root_dir_tree[tit] = RootTree(self, columns=('fullpath','type','size'),
            displaycolumns='size', root_dir=self.root_dir[tit],
            conn=self.ftp_conn if tit=='Remote' else None)
        print(tit, self.root_dir_tree[tit])

        yScrollBar = ttk.Scrollbar(self.root_dir_tree[tit], orient=constants.VERTICAL,
            command=self.root_dir_tree[tit].yview)
        xScrollBar = ttk.Scrollbar(self.root_dir_tree[tit], orient=constants.HORIZONTAL,
            command=self.root_dir_tree[tit].xview)
        self.root_dir_tree[tit]['yscroll'] = yScrollBar.set
        self.root_dir_tree[tit]['xscroll'] = xScrollBar.set

        self.root_dir_tree[tit].heading('#0', text='Directory', anchor=constants.W)
        self.root_dir_tree[tit].heading('size', text='Size', anchor=constants.W)
        self.root_dir_tree[tit].column('size', stretch=0, width=40)

        self.dir_tree_frame[tit].grid(row=rw, column=cl, sticky=constants.W, pady=4, padx=5)
        ttk.Label(self.dir_tree_frame[tit], text=tit).grid(row=rw, column=cl, sticky=constants.W)
        self.root_dir_tree[tit].grid(in_=self.dir_tree_frame[tit], row=rw+1, column=cl,
            sticky=constants.NSEW)
        # yScrollBar.grid(row=rw+1, column=cl+3, sticky=constants.NS)
        # xScrollBar.grid(row=rw+3, column=cl, sticky=constants.EW)
        # set frame resizing priorities
        # self.dir_tree_frame[tit].rowconfigure(0, weight=1)
        # self.dir_tree_frame[tit].columnconfigure(0, weight=1)

    # Enable this frame later
    # def create_stdout_frame(self, rw, cl):
    #     self.stdout_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
    #     self.stdout_frame.grid(row=rw, column=cl)
    #
    #     self.old_stdout = sys.stdout
    #     self.text = tkinter.Text(self, width=40, height=10, wrap='none')
    #     self.text.grid(row=rw+1, column=cl)
    #     sys.stdout = StdoutRedirector(self.text)

    # Enable this frame later
    # def create_stderr_frame(self, rw, cl):
    #     self.stderr_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
    #     self.stderr_frame.grid(row=rw, column=cl)
    #
    #     self.old_stderr = sys.stderr
    #
    #     self.err = tkinter.Text(self, width=60, height=10, wrap='none')
    #     self.err.grid(row=rw+1, column=cl+1)
    #     sys.stderr = StdoutRedirector(self.err)

    def select_dir(self, dir_tree_view):
        if isinstance(dir_tree_view, RootTree):
            children = dir_tree_view.get_children('')
            if children:
                dir_tree_view.delete(children)
            dir_tree_view.root_directory.set(filedialog.askdirectory().replace("/" , str(os.sep)))

if __name__ == '__main__':
    root = tkinter.Tk()
    app = FTPClientApp(master=root)
    app.mainloop()
    try:
        app.ftp_conn.disconnect(self.root_dir_tree['Local'])
    except:
        pass

    # sys.stdout = app.old_stdout
    # sys.stderr = app.old_stderr
