#!/usr/bin/python3
# serverGUI.py

VERSION = "0.0 RELEASE"
import os, tkinter, threading, sys, re
from functools import partial
from tkinter import ttk, constants, filedialog
import pdb

import ftplib

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer

class FTPServerClientApp(tkinter.Frame):
    root_dir = dict()
    root_dir_tree = dict()
    dir_tree_frame = dict()
    ftp_conn = ftplib.FTP()

    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.grid(row=0, column=0)

        # May need to move this out
        self.authorizer = DummyAuthorizer()
        self.initialise()

        # Main Frame
        # master.geometry("480x120")
        master.minsize(960,640)
        master.title("FTP Server")

        # Grid Position (row, column)
        # self.grid_pstn={(row:, column: }

        self.create_server_control_frame()
        self.create_start_button()
        self.create_stop_button()

        self.create_state_frame()
        self.create_input_frame()

        self.create_remote_dir_button()
        self.create_connect_button()

        self.create_dir_frame()
        self.create_dir_tree_frame(7, 0, "Local")
        self.create_push_file_button()

        self.create_dir_tree_frame(7, 4, "Remote")
        self.create_pull_file_button()

        self.create_browse_button()
        self.create_share_button()

        self.create_stdout_frame()
        # self.create_stderr_frame()

        self.handler = FTPHandler
        self.handler.authorizer = self.authorizer
        self.handler.banner = "FTP Server ver %s is ready" % VERSION #does this work in Python3?

    def create_server_control_frame(self):
        # Server Control Frame
        self.server_control_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.server_control_frame.grid(row=0, column=0, columnspan=4)
        ttk.Label(self.server_control_frame, text="Server Control ").grid(row=0, column=0)

    def create_start_button(self):
        self.start_button = ttk.Button(self.server_control_frame, text="Start",
            command=self.start_server)
        self.start_button.grid(row=0, column=2)

    def create_stop_button(self):
        self.stop_button = ttk.Button(self.server_control_frame, text="Stop", state=['disabled'],
                        command=self.stop_server)
        self.stop_button.grid(row=0, column=3)

    def create_state_frame(self):
        # State Frame
        state_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        state_frame.grid(row=1, column=0, columnspan=3)
        ttk.Label(state_frame, text="Server State").grid(row=1, column=0)

        state_value = ttk.Label(state_frame, textvariable=self.current_state, foreground='blue')
        state_value.grid(row=1, column=2)

    def create_input_frame(self):
        self.input_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.input_frame.grid(row=3, column=0, columnspan=3)

        # ttk.Label(self.input_frame, text="User Name").grid(row=2, column=0)
        # self.username_input = ttk.Entry(self.input_frame, textvariable=self.username)
        # self.username_input.grid(row=3, column=0)

        # ttk.Label(self.input_frame, text="Password").grid(row=2, column=1)
        # self.password_input = ttk.Entry(self.input_frame, textvariable=self.password)
        # self.password_input.grid(row=3, column=1)

        ttk.Label(self.input_frame, text="Server Address").grid(row=2, column=2)
        self.listen_ip_input = ttk.Entry(self.input_frame, textvariable=self.listen_ip)
        self.listen_ip_input.grid(row=3, column=2)

        ttk.Label(self.input_frame, text="Server Port").grid(row=2, column=3)
        self.listen_port_input = ttk.Entry(self.input_frame, textvariable=self.listen_port)
        self.listen_port_input.grid(row=3, column=3)

    def create_dir_frame(self):
        self.dir_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.dir_frame.grid(row=4, column=0, columnspan=3)

        ttk.Label(self.dir_frame, text="Shared Directory").grid(row=4, column=0)

        # TODO: Rename this to Local root dir later.
        # Now still cannot imagine how to get the remote root directory and display the tree
        self.root_dir_input = ttk.Entry(self.dir_frame, width=64,
            textvariable=self.root_dir['Local'])
        self.root_dir_input.grid(row=5, column=0)

    def create_browse_button(self):
        self.browse_button = ttk.Button(self.dir_frame, text="Browse",
            command=partial(self.select_dir, self.root_dir_tree['Local']))
        self.browse_button.grid(row=5, column=4)

    def create_share_button(self):
        self.share_button = ttk.Button(self.dir_frame, text="Share",
            command=partial(self.share_dir, self.root_dir_tree['Local']))
        self.share_button.grid(row=5, column=5)

    def create_push_file_button(self):
        self.push_file_button = ttk.Button(self.dir_tree_frame['Local'], text="Push >>",
            command=self.push_file)
        self.push_file_button.grid(row=0)

    def create_pull_file_button(self):
        self.pull_file_button = ttk.Button(self.dir_tree_frame['Remote'], text="Pull <<",
            command=self.pull_file)
        self.pull_file_button.grid(row=0)

    def connect(self):
        user = self.username.get()
        pswd = self.password.get()
        try:
            self.ftp_conn = ftplib.FTP(user=user, passwd=pswd)
            self.ftp_conn.connect(host=self.listen_ip.get(), port=int(self.listen_port.get()))
            self.ftp_conn.login(user, pswd)
        except:
            print("Login failed, check username, password, IP and port.")
            return

        self.root_dir_tree['Remote'].root_directory.set(str(os.sep))

    def create_remote_dir_button(self):
        self.remote_dir_button = ttk.Button(self, text="Remote Dir",
            command=self.list_remote_dir)
        self.remote_dir_button.grid(row=0, column=2)

    def create_connect_button(self):
        self.connect_button = ttk.Button(self, text="Connect", command=self.connect)
        self.connect_button.grid(row=0, column=3)

    def upload_file(filename, outfile=None):
        if not outfile:
            outfile = sys.stdout
        if re.search('\.txt$', filename):
            self.ftp_conn.storlines("STOR " + filename, open(filename))
        else:
            self.ftp_conn.storbinary("STOR " + filename, open(filename, "rb"), 1024)

    def get_file(filename, outfile=None):
        if not outfile:
            outfile = sys.stdout
        if re.search('\.txt$', filename):
            self.ftp_conn.retrlines("RETR " + filename, lambda s, w=outfile.write: w(s+"\r\n"))
        else:
            self.ftp_conn.retrbinary("RETR " + filename, outfile.write)

    def list_remote_dir(self):
        dat = []   # TODO: What if there are more than 2 instances running on the same comp?
        self.ftp_conn.dir(dat.append)
        self.root_dir_tree['Remote'].populate_parent()
        for fil in dat:
            print(fil)

    def push_file(self):
        files = self.root_dir_tree['Local'].selection()
        for fil in files:
            print(fil)
            # self.upload_file(conn, file)

    def pull_file(self):
        files = self.root_dir_tree['Remote'].selection()
        for fil in files:
            print(fil)
            # self.getfile(conn, file)

    def create_dir_tree_frame(self, rw, cl, tit):
        self.dir_tree_frame[tit] = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.dir_tree_frame[tit].grid(row=rw, column=cl, rowspan=4, columnspan=4)
        ttk.Label(self.dir_tree_frame[tit], text=tit).grid(row=max(0,rw-1), column=0)

        # TODO: do i need to Check tit is not None here?
        self.root_dir_tree[tit] = RootTree(self, columns=('fullpath','type','size'),
            displaycolumns='size', root_dir=self.root_dir[tit],
            conn=self.ftp_conn if tit=='Remote' else None)
        yScrollBar = ttk.Scrollbar(orient=constants.VERTICAL, command=self.root_dir_tree[tit].yview)
        xScrollBar = ttk.Scrollbar(orient=constants.HORIZONTAL,
            command=self.root_dir_tree[tit].xview)
        self.root_dir_tree[tit]['yscroll'] = yScrollBar.set
        self.root_dir_tree[tit]['xscroll'] = xScrollBar.set

        self.root_dir_tree[tit].heading('#0', text='Directory', anchor=constants.W)
        self.root_dir_tree[tit].heading('size', text='Size', anchor=constants.W)
        self.root_dir_tree[tit].column('size', stretch=0, width=40)

        self.root_dir_tree[tit].grid(row=rw+1, column=cl, sticky=constants.NSEW)
        yScrollBar.grid(row=rw+1, column=cl+1, sticky=constants.NS)
        xScrollBar.grid(row=rw+2, column=cl, sticky=constants.EW)

    def create_stdout_frame(self):
        self.stdout_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.stdout_frame.grid(row=12, column=0)

        self.old_stdout = sys.stdout
        self.text = tkinter.Text(self, width=40, height=10, wrap='none')
        self.text.grid(row=13, column=0)
        sys.stdout = StdoutRedirector(self.text)

    # Enable this frame later
    # def create_stderr_frame(self):
    #     self.stderr_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
    #     self.stderr_frame.grid(row=12, column=1)
    #
    #     self.old_stderr = sys.stderr
    #
    #     self.err = tkinter.Text(self, width=60, height=10, wrap='none')
    #     self.err.grid(row=13, column=1)
    #     sys.stderr = StdoutRedirector(self.err)

    def initialise(self):
        # Initial values
        self.username = tkinter.StringVar()
        self.username.set("user")

        self.password = tkinter.StringVar()
        self.password.set("passwd")

        self.root_dir['Local'] = tkinter.StringVar()
        self.root_dir['Local'].set(os.getcwd() + os.sep)

        self.current_state = tkinter.StringVar()
        self.current_state.set("not running")

        self.listen_ip = tkinter.StringVar()
        self.listen_ip.set("127.0.0.1")

        self.listen_port = tkinter.StringVar()
        self.listen_port.set("21")

        self.root_dir['Remote'] = tkinter.StringVar()
        self.root_dir['Remote'].set(os.sep)

        # This can be set up only once and saved in a database
        self.authorizer.add_user(self.username.get(), self.password.get(),
            self.root_dir['Local'].get(), 'elradfmw')

    def start_server(self):
        self.address = ("127.0.0.1", int(21))

        self.server = ThreadedFTPServer(self.address, self.handler)
        self.server.max_cons = 256
        self.server.max_cons_per_ip = 5

        self.address = (self.listen_ip.get(), int(self.listen_port.get()))
        print("Connected to", self.address)
        self.start_button.state(['disabled'])
        self.stop_button.state(['!disabled'])
        self.current_state.set("RUNNING")
        # self.server.serve_forever() # WARNING: Must find a way to prevent this from blocking!
        threading.Thread(target=self.server.serve_forever).start()
        print(self.username.get(), self.password.get())

    def stop_server(self):
        self.server.close_all()
        # self.authorizer.remove_user(self.username.get())
        self.start_button.state(['!disabled'])
        self.stop_button.state(['disabled'])
        self.current_state.set("NOT RUNNING")

    def select_dir(self, dir_tree_view):
        if isinstance(dir_tree_view, RootTree):
            children = dir_tree_view.get_children('')
            if children:
                dir_tree_view.delete(children)
            dir_tree_view.root_directory.set(filedialog.askdirectory().replace("/" , str(os.sep)))

    def share_dir(self, dir_tree_view):
        if isinstance(dir_tree_view, RootTree):
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

class RootTree(ttk.Treeview):
    ftp_conn = None
    def __init__(self, *args, root_dir, conn, **kwargs):
        super(RootTree, self).__init__(*args, **kwargs)
        assert isinstance(root_dir, tkinter.StringVar)
        self.root_directory = root_dir
        if conn:
            assert isinstance(conn, ftplib.FTP)
            self.ftp_conn = conn
        self.bind('<<TreeviewOpen>>', self.update_tree)

    def list_dir(self, dir_path):
        if self.ftp_conn:
            return self.ftp_conn.nlst(dir_path)
        else:
            return os.listdir(dir_path)

    def get_file_size(self, filename):
        if self.ftp_conn:
            return self.ftp_conn.size(filename)
        else:
            return os.stat(filename).st_size

    def populate_tree(self, parent, fullpath, children):
        for child in children:
            child_path = os.path.join(fullpath, child).replace('\\', '/')
            if os.path.isdir(child_path):
                child_id = self.insert(parent, constants.END, text=child,
                    values=[child_path, 'directory'])
                self.insert(child_id, constants.END, text='dummy')
            else:
                filesize = self.get_file_size(child_path)
                self.insert(parent, constants.END, text=child,
                    values=[child_path, 'directory', filesize])

    def populate_parent(self):
        if self.root_directory:
            curr_dir = self.root_directory.get()
            print(curr_dir)
            if self.ftp_conn:
                os.path.split(curr_dir)

            parent = self.insert('', constants.END, text=curr_dir, values=[curr_dir, 'directory'])
            self.populate_tree(parent, curr_dir, self.list_dir(curr_dir))

    def update_tree(self, event):
        # event: unused variable
        node_id = self.focus()
        if self.parent(node_id):
            # TODO: double click cause warning, but either need to bind it with another action
            # or replace with a try catch block later
            top_child = self.get_children(node_id)[0]
            if self.item(top_child, option='text') == 'dummy':
                self.delete(top_child)
                tree_path = self.set(node_id, 'fullpath')
                self.populate_tree(node_id, tree_path, self.list_dir(tree_path))

class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert('end', string)
        self.text_space.see('end')

if __name__ == '__main__':
    root = tkinter.Tk()
    app = FTPServerClientApp(master=root)
    app.mainloop()
    try:
        app.server.close_all()
    except:
        pass

    sys.stdout = app.old_stdout
    # sys.stderr = app.old_stderr
