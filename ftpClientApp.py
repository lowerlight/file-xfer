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
BLOCK_SIZE = 1024
LOWEST_PORT_NO = 1025
HIGHEST_PORT_NO = 65533

import os, tkinter, threading, sys, time, re, socket, ipaddress
from functools import partial
from tkinter import ttk, constants, filedialog
import tkinter.messagebox as mbox
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
        # Main Frame
        master.minsize(960,640)
        self.local_ip_addr = socket.gethostbyname(socket.getfqdn())
        master.title("FTP Client by TP031319 at %s" % self.local_ip_addr)

        self.initialise()

        self.create_control_frame(rw=0, cl=0)

        self.create_state_frame(rw=1, cl=0)
        self.create_input_frame(rw=0, cl=3)

        self.create_remote_dir_button(rw=1, cl=3)

        self.create_dir_frame(rw=3, cl=0)
        self.create_dir_tree_frame(rw=7, cl=0, tit="Local")
        self.create_push_file_button(rw=7, cl=1)

        self.create_dir_tree_frame(rw=7, cl=3, tit="Remote")
        self.create_pull_file_button(rw=7, cl=2)

        self.create_connect_button(rw=0, cl=1)
        self.create_disconnect_button(rw=0, cl=2)

        self.create_browse_button(rw=4, cl=3)
        self.create_share_button(rw=4, cl=4)

        self.create_stdout_frame(rw=8, cl=0)

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
        self.listen_port.set(str(LOWEST_PORT_NO))

        self.root_dir['Remote'] = tkinter.StringVar()
        self.root_dir['Remote'].set(os.sep)

        self.transferred_up_to_now = 0
        self.filesize_in_transfer = 0

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

        ttk.Label(self.input_frame, text="Server Address").grid(row=rw, column=cl,
            sticky=constants.W)
        self.listen_ip_input = ttk.Entry(self.input_frame, width=40, textvariable=self.listen_ip)
        self.listen_ip_input.grid(row=rw+1, column=cl)

        ttk.Label(self.input_frame, text="Server Port").grid(row=rw, column=cl+1,
            sticky=constants.W)
        self.listen_port_input = ttk.Entry(self.input_frame, width=8, textvariable=self.listen_port)
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
        self.share_button = ttk.Button(self.dir_frame, text="Refresh Local",
            command=partial(self.share_dir, self.root_dir_tree['Local']))
        self.share_button.grid(row=rw, column=cl)

    def create_dir_frame(self, rw, cl):
        self.dir_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.dir_frame.grid(row=rw, column=cl, columnspan=2, sticky=constants.W, pady=4, padx=5)
        ttk.Label(self.dir_frame, text="Local Directory").grid(row=rw, column=cl,
            sticky=constants.W)

        self.root_dir_input = ttk.Entry(self.dir_frame, width=64,
            textvariable=self.root_dir['Local'])
        self.root_dir_input.grid(row=rw+1, column=cl)

    def create_push_file_button(self, rw, cl):
        self.push_file_button = ttk.Button(self, text="Upload >>", state=['disabled'],
            command=self.push_file)
        self.push_file_button.grid(row=rw, column=cl)

    def create_pull_file_button(self, rw, cl):
        self.pull_file_button = ttk.Button(self, text="Download <<", state=['disabled'],
            command=self.pull_file)
        self.pull_file_button.grid(row=rw, column=cl)

    def list_remote_dir(self):
        assert isinstance(self.root_dir_tree['Remote'], RootTree)
        self.reconnect()
        self.root_dir['Remote'].set(self.ftp_conn.pwd())
        self.root_dir_tree['Remote'].root_directory = self.root_dir['Remote']
        self.root_dir_tree['Remote'].populate_parent()

    def connect(self):
        user = self.username.get()
        pswd = self.password.get()

        port_no = 0
        msg = "Please type a valid IP and a port number between 1025 and 65533 inclusive."
        try:
            host = self.listen_ip.get()
            port_no = int(self.listen_port.get())

            if port_no < LOWEST_PORT_NO or port_no > HIGHEST_PORT_NO:
                msg += " Port {0} is not valid.".format(port_no)
                raise Exception(msg)

            msg += " IPv4 and IPv6 are accepted, but {0} is not valid.".format(host)
            ipaddress.ip_address(host)  # throw Exception for invalid IP
        except:
            mbox.showinfo(message=msg)
            return

        try:
            self.ftp_conn = ftplib.FTP(user=user, passwd=pswd)
            print("h1")
            self.ftp_conn.connect(host=host, port=port_no)
            print((host, port_no))
            print("h2")
            self.ftp_conn.login(user, pswd)
            print("h3")
        except:
            mbox.showinfo(message="Connecting failed, please check IP and port.")
            return

        self.share_dir(self.root_dir_tree['Local'])
        self.list_remote_dir()
        # self.ftp_conn.set_debuglevel(2)

        self.connect_button.state(['disabled'])
        self.disconnect_button.state(['!disabled'])
        self.remote_dir_button.state(['!disabled'])
        self.push_file_button.state(['!disabled'])
        self.pull_file_button.state(['!disabled'])
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
            self.remote_dir_button.state(['disabled'])
            self.push_file_button.state(['disabled'])
            self.pull_file_button.state(['disabled'])
            self.current_state.set("DISCONNECTED")

            if isinstance(dir_tree_view, RootTree):
                children = dir_tree_view.get_children('')
                if children:
                    dir_tree_view.delete(children)

    def reconnect(self):
        user = self.username.get()
        pswd = self.password.get()
        host = self.listen_ip.get()
        port = int(self.listen_port.get())

        # print(self.root_dir_tree['Remote'].ftp_conn.sock)   # TO ANSWER: why the sock go missing?!
        if not self.root_dir_tree['Remote'].ftp_conn.sock:
            self.root_dir_tree['Remote'].ftp_conn.connect(host=host, port=port)
            # print("Reconnected!")
            self.root_dir_tree['Remote'].ftp_conn.login(user=user, passwd=pswd)
            # print("Reloggedin!")

    def create_remote_dir_button(self, rw, cl):
        self.remote_dir_button = ttk.Button(self, text="Refresh Remote", state=['disabled'],
            command=self.list_remote_dir)
        self.remote_dir_button.grid(row=rw, column=cl, sticky=constants.W, pady=4, padx=5)

    def share_dir(self, dir_tree_view):
        if isinstance(dir_tree_view, RootTree):
            try:
                os.chdir(self.root_dir['Local'].get())
                dir_tree_view.root_directory = self.root_dir['Local']
                if dir_tree_view.ftp_conn:
                    dir_tree_view.ftp_conn.reconnect()
                    dir_tree_view.ftp_conn.cwd(self.root_dir['Local'].get())
                dir_tree_view.populate_parent()
            except FileNotFoundError:
                mbox.showinfo(message="Invalid Directory!")

    def select_dir(self, dir_tree_view):
        if isinstance(dir_tree_view, RootTree):
            children = dir_tree_view.get_children('')
            if children:
                dir_tree_view.delete(children)
            old_dir_tree_view_root_dir = dir_tree_view.root_directory.get()
            dir_tree_view.root_directory.set(filedialog.askdirectory().replace("/" , str(os.sep)))
            if not dir_tree_view.root_directory.get():
                dir_tree_view.root_directory.set(old_dir_tree_view_root_dir)

    def progress_counter(self, buf):
        # Do nothing to the buf being transferred
        self.transferred_up_to_now += self.block_size
        print("{0:.2f}% completed".format(
            min(self.transferred_up_to_now/self.filesize_in_transfer*100.00, 100.00)))

    def upload_file(self, filename, outfile=None):
        self.block_size = BLOCK_SIZE
        start_time = 0
        if not outfile:
            outfile = sys.stdout
        self.reconnect()
        print("Uploading {0}".format(filename))
        filename_without_path = os.path.split(filename)[1]
        if re.search('\.txt$', filename):
            self.ftp_conn.storlines("STOR " + filename_without_path, open(filename),
                self.progress_counter)
                # default mode for open() is "rt" so not mentioned
        else:
            start_time = time.time()
            self.ftp_conn.storbinary("STOR " + filename_without_path, open(filename, "rb"),
                BLOCK_SIZE, self.progress_counter)
        print("{0} bytes uploaded in {1:.2f} seconds".format(self.filesize_in_transfer,
            (time.time() - start_time)))
        self.transferred_up_to_now = 0

    def download_file(self, filename, outfile=None):
        self.block_size = 8*BLOCK_SIZE  # It's possible to download 8* upload speed
        start_time = 0
        if not outfile:
            outfile = sys.stdout
        else:
            # TODO: Check if file already exists and append number?/alert user?
            pass

        self.reconnect()
        print("Downloading {0}".format(filename))
        if re.search('\.txt$', filename):
            outfile = open(filename, 'w')
            self.ftp_conn.retrlines("RETR " + filename,
                lambda s, w=outfile.write: w(s+"\r\n"))
        else:
            outfile = open(filename, 'wb')

            def write_and_count(buf):
                outfile.write(buf)
                self.progress_counter(buf)
            start_time = time.time()
            self.ftp_conn.retrbinary("RETR " + filename, write_and_count, self.block_size)
        outfile.close()
        print("{0} bytes downloaded in {1:.2f} seconds".format(self.filesize_in_transfer,
            (time.time() - start_time)))
        self.transferred_up_to_now = 0

    def push_file(self):
        files = self.root_dir_tree['Local'].selection()
        for fileinfo in files:
            file_details = self.root_dir_tree['Local'].item(fileinfo, 'values')
            self.filesize_in_transfer = int(file_details[2])
            self.upload_file(file_details[0])
            self.filesize_in_transfer = 0

    def pull_file(self):
        files = self.root_dir_tree['Remote'].selection()
        for fileinfo in files:
            file_details = self.root_dir_tree['Remote'].item(fileinfo, 'values')
            self.filesize_in_transfer = int(file_details[2])
            self.download_file(file_details[0])
            self.filesize_in_transfer = 0

    def create_dir_tree_frame(self, rw, cl, tit):
        self.dir_tree_frame[tit] = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.root_dir_tree[tit] = RootTree(self, columns=('fullpath','type','size'),
            displaycolumns='size', root_dir=self.root_dir[tit],
            conn=self.ftp_conn if tit=='Remote' else None)

        self.root_dir_tree[tit].heading('#0', text='Directory', anchor=constants.W)
        self.root_dir_tree[tit].heading('size', text='Size', anchor=constants.W)
        self.root_dir_tree[tit].column('#0', stretch=0, minwidth=120, width=280)
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

    # Enable this frame later
    def create_stdout_frame(self, rw, cl):
        self.stdout_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.stdout_frame.grid(row=rw, column=cl)

        self.old_stdout = sys.stdout
        self.text = tkinter.Text(self, width=64, height=12, wrap='none')
        self.text.grid(row=rw+1, column=cl, pady=4, padx=5)
        sys.stdout = StdoutRedirector(self.text)

if __name__ == '__main__':
    root = tkinter.Tk()
    app = FTPClientApp(master=root)
    app.mainloop()
    try:
        app.ftp_conn.disconnect(self.root_dir_tree['Local'])
    except:
        pass

    sys.stdout = app.old_stdout
    # sys.stderr = app.old_stderr
