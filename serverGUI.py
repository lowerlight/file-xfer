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

        self.create_server_control_frame(rw=0, cl=0)

        self.create_state_frame(rw=1, cl=0)
        self.create_input_frame(rw=3, cl=0)

        self.create_connect_button(rw=0, cl=3)
        self.create_remote_dir_button(rw=1, cl=3)

        self.create_disconnect_button(rw=2, cl=3)

        self.create_dir_frame(rw=4, cl=0)
        self.create_dir_tree_frame(rw=7, cl=0, tit="Local")
        self.create_push_file_button(rw=7, cl=1)

        self.create_dir_tree_frame(rw=7, cl=4, tit="Remote")
        self.create_pull_file_button(rw=7, cl=2)

        self.create_browse_button(rw=5, cl=4)
        self.create_share_button(rw=5, cl=5)

        # self.create_stdout_frame(rw=8, cl=0)
        # self.create_stderr_frame(rw=8, cl=1)

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

    def create_dir_frame(self, rw, cl):
        self.dir_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.dir_frame.grid(row=rw, column=cl, columnspan=3, sticky=constants.W, pady=4, padx=5)
        ttk.Label(self.dir_frame, text="Shared Directory").grid(row=rw, column=cl,
            sticky=constants.W)

        # TODO: Rename this to Local root dir later.
        # Now still cannot imagine how to get the remote root directory and display the tree
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

    def create_push_file_button(self, rw, cl):
        self.push_file_button = ttk.Button(self, text="Push >>",
            command=self.push_file)
        self.push_file_button.grid(row=rw, column=cl)

    def create_pull_file_button(self, rw, cl):
        self.pull_file_button = ttk.Button(self, text="Pull <<",
            command=self.pull_file)
        self.pull_file_button.grid(row=rw, column=cl)

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

    def disconnect(self):
        user = self.username.get()
        pswd = self.password.get()
        host = self.listen_ip.get()
        port = int(self.listen_port.get())

        try:
             self.ftp_conn.quit()
        except:
            print("Already disconnected")

    def create_remote_dir_button(self, rw, cl):
        self.remote_dir_button = ttk.Button(self, text="Remote Dir",
            command=self.list_remote_dir)
        self.remote_dir_button.grid(row=rw, column=cl)

    def create_connect_button(self, rw, cl):
        self.connect_button = ttk.Button(self, text="Connect", command=self.connect)
        self.connect_button.grid(row=rw, column=cl)

    def create_disconnect_button(self, rw, cl):
        self.connect_button = ttk.Button(self, text="Disconnect", command=self.disconnect)
        self.connect_button.grid(row=rw, column=cl)

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

    def list_remote_dir(self):
        assert isinstance(self.root_dir_tree['Remote'], RootTree)
        self.reconnect()
        self.root_dir_tree['Remote'].populate_parent()

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

    def initialise(self):
        # Initial values
        self.username = tkinter.StringVar()
        self.username.set("user")

        self.password = tkinter.StringVar()
        self.password.set("passwd")

        self.root_dir['Local'] = tkinter.StringVar()
        self.root_dir['Local'].set(os.getcwd() + os.sep)

        self.current_state = tkinter.StringVar()
        self.current_state.set("NOT RUNNING")

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

class RootTree(ttk.Treeview):
    ftp_conn = None
    ftp_item_dict = dict()
    def __init__(self, *args, root_dir, conn, **kwargs):
        super(RootTree, self).__init__(*args, **kwargs)
        assert isinstance(root_dir, tkinter.StringVar)
        self.root_directory = root_dir
        if conn:
            assert isinstance(conn, ftplib.FTP)
            print("Assigning connection")
            self.ftp_conn = conn
        self.bind('<<TreeviewOpen>>', self.update_tree)

    def list_dir(self, dir_path):
        if self.ftp_conn:
            # Just let the server determine the current path, don't pump in any path
            ftp_returned_gen = self.ftp_conn.mlsd(facts=['size'])
            for i in ftp_returned_gen:
                self.ftp_item_dict[i[0]] = i[1]['size']
            return self.ftp_item_dict.keys()
        else:
            return os.listdir(dir_path)

    def get_file_size(self, filename):
        if self.ftp_conn:
            filename.lstrip(os.sep)
            return self.ftp_item_dict[filename]
        else:
            return os.stat(filename).st_size

    def populate_tree(self, parent, fullpath, children):
        for child in children:
            if self.ftp_conn:
                child_path = child
            else:
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
            # Need to delete previous parent if exists
            children = self.get_children('')
            if children:
                self.delete(children)
                self.ftp_item_dict.clear()

            curr_dir = self.root_directory.get()
            print(curr_dir)
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

    # sys.stdout = app.old_stdout
    # sys.stderr = app.old_stderr
