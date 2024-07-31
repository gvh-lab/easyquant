#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 15:22:28 2024

@author: justin

"""

import tkinter as tk

class ScrollListBox(tk.Frame):
    """
    The scroll box inside the FileManagerWindow and associated file functions.

    Attributes:
        file_manager: An object which keeps track of the files and their
                      associated QuantData objects.
        listbox: The displayed box listing the files that have been imported.
        scrollbar: The scroll bar on the side of the listbox.
    """
    def __init__(self, file_manager_window, file_manager):

        # Initialize the tk.Frame and tell it which window contains this frame.
        tk.Frame.__init__(self, file_manager_window)
        self.pack(expand=tk.YES, fill=tk.BOTH)


        self.file_manager = file_manager
        self.file_manager_window = file_manager_window


        # Setup listbox
        self.listbox = tk.Listbox(self, relief=tk.SUNKEN, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)


        # Setup scrollbar
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        # Attach scrollbar and listbox
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)


        # Binds the opening method to a double click ('<Double-1>' in tkinter)
        self.listbox.bind('<Double-1>', self.open_from_event)


    def update(self):
        """
        Pulls names from the file-manager's qd_list and populates the listbox.
        """
        self.clear_listbox()
        for qd in self.file_manager.qd_list:
            self.add_filename_to_listbox(qd.base)


    def open_from_event(self, event: tk.EventType) -> None:
        """
        Wrapper method to handle events. Passes to open_file_from_index.

        Note:
        - Event needs to be the first optional argument, since it's passed in
          automatically by listbox.bind.
        """
        index = self.get_index_of_selected()
        self.file_manager.set_active_index(index)


    def import_files(self):
        """
        Tells the file manager to import files.
        Tells the window to set a message.
        Tells the scroll_list_box (self) to pull filenames from file manager.
        """
        self.file_manager.import_files()
        self.file_manager_window.set_message("Double click to open.")
        self.update()


    def get_index_of_selected(self) -> int:
        index_list = self.listbox.curselection()
        if not index_list:
            print("Error opening file: Nothing selected.")
        else:
            index = index_list[0]
            return index

    def clear_listbox(self) -> None:
        self.listbox.delete(0, tk.END)

    def add_filename_to_listbox(self, name: str) -> None:
        self.listbox.insert(tk.END, name)