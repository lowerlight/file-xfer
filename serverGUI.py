#!/usr/bin/python3
# serverGUI.py

VERSION = "0.0 RELEASE"
import os, tkinter, threading
from tkinter import ttk, constants, filedialog

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer

class ServerApp(tkinter.Frame):
    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.grid(row=0, column=0)

        # May need to move this out
        self.authorizer = DummyAuthorizer()
        self.initialise()

        # Main Frame
        # master.geometry("480x120")
        master.minsize(960,480)
        master.title("FTP Server")

        # Grid Position (row, column)
        # self.grid_pstn={(row:, column: }

        self.create_server_control_frame()
        self.create_start_button()
        self.create_stop_button()

        self.create_state_frame()
        self.create_input_frame()

        self.create_dir_frame()
        self.create_browse_button()

        self.create_dirTree_frame()

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

        self.root_dir_input = ttk.Entry(self.dir_frame, width=64, textvariable=self.root_dir)
        self.root_dir_input.grid(row=5, column=0)

    def create_browse_button(self):
        self.browse_button = ttk.Button(self.dir_frame, text="Browse",
            command=self.select_dir)
        self.browse_button.grid(row=5, column=4)

    def populate_tree(self, parent, fullpath, children):
        for child in children:
            child_path = os.path.join(fullpath, child).replace('\\', '/')
            if os.path.isdir(child_path):
                child_id = self.root_dirTree.insert(parent, constants.END, text=child,
                    values=[child_path, 'directory'])
                self.root_dirTree.insert(child_id, constants.END, text='dummy')
            else:
                filesize = os.stat(child_path).st_size
                self.root_dirTree.insert(parent, constants.END, text=child,
                    values=[child_path, 'directory', filesize])

    def populate_parent(self):
        curr_dir = self.root_dir.get()
        parent = self.root_dirTree.insert('', constants.END, text=curr_dir,
            values=[curr_dir, 'directory'])
        self.populate_tree(parent, curr_dir, os.listdir(curr_dir))

    def update_tree(self, event):
        # event: unused variable
        node_id = self.root_dirTree.focus()
        if self.root_dirTree.parent(node_id):
            # TODO: double click cause warning, but either need to bind it with another action
            # or replace with a try catch block later
            top_child = self.root_dirTree.get_children(node_id)[0]
            if self.root_dirTree.item(top_child, option='text') == 'dummy':
                self.root_dirTree.delete(top_child)
                tree_path = self.root_dirTree.set(node_id, 'fullpath')
                self.populate_tree(node_id, tree_path, os.listdir(tree_path))

    def create_dirTree_frame(self):
        self.dirTree_frame = ttk.Frame(self, relief=constants.SOLID, borderwidth=1)
        self.dirTree_frame.grid(row=7, column=0, rowspan=4, columnspan=8)

        ttk.Label(self.dirTree_frame, text="Local").grid(row=6, column=0)

        self.root_dirTree = ttk.Treeview(columns=('fullpath','type','size'), displaycolumns='size')
        yScrollBar = ttk.Scrollbar(orient=constants.VERTICAL, command=self.root_dirTree.yview)
        xScrollBar = ttk.Scrollbar(orient=constants.HORIZONTAL, command=self.root_dirTree.xview)
        self.root_dirTree['yscroll'] = yScrollBar.set
        self.root_dirTree['xscroll'] = xScrollBar.set

        self.root_dirTree.heading('#0', text='Directory', anchor=constants.W)
        self.root_dirTree.heading('size', text='Size', anchor=constants.W)

        self.root_dirTree.column('size', stretch=0, width=70)

        self.root_dirTree.grid(row=8, column=0, sticky=constants.NSEW)
        yScrollBar.grid(row=8, column=1, sticky=constants.NS)
        xScrollBar.grid(row=9, column=0, sticky=constants.EW)

        self.populate_parent()
        self.root_dirTree.bind('<<TreeviewOpen>>', self.update_tree)

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

        # This can be set up only once and saved in a database
        self.authorizer.add_user(self.username.get(), self.password.get(), self.root_dir.get(),
            'elradfmw')

    def start_server(self):
        self.address = ("127.0.0.1", int(21))

        self.server = ThreadedFTPServer(self.address, self.handler)
        self.server.max_cons = 256
        self.server.max_cons_per_ip = 5

        self.address = (self.listen_ip.get(), int(self.listen_port.get()))
        print(self.address)
        self.start_button.state(['disabled'])
        self.stop_button.state(['!disabled'])
        self.current_state.set("RUNNING")
        # self.server.serve_forever() # WARNING: Must find a way to prevent this from blocking!
        threading.Thread(target=self.server.serve_forever).start()

    def stop_server(self):
        self.server.close_all()
        # self.authorizer.remove_user(self.username.get())
        self.start_button.state(['!disabled'])
        self.stop_button.state(['disabled'])
        self.current_state.set("NOT RUNNING")

    def select_dir(self):
        # Delete old root_dir
        self.root_dirTree.delete(self.root_dirTree.get_children(''))

        self.root_dir.set(filedialog.askdirectory().replace("/" , str(os.sep)))

        # Attach new root_dir
        self.populate_parent()

if __name__ == '__main__':
    root = tkinter.Tk()
    app = ServerApp(master=root)
    app.mainloop()
    try:
        app.server.close_all()
    except:
        pass
