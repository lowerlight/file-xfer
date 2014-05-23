#!/usr/bin/python3
# ftpGUI.py

"""
Project : Network Programming Assignment Question
Filename : ftpGUI.py
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
import tkinter, ftplib, os
from tkinter import ttk, constants, filedialog

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
