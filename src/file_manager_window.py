#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 21:00:14 2024

@author: justin
"""

import tkinter as tk
from typing import Callable
from src import scroll_list_box
from src import message_bar


class FileManagerWindow(tk.Frame):
    """
    This is the first window to open when the program is run.
    Is a scroll box with an import button and a list of files.
    Allows importing and displays which files have been imported.
    This only handles initializing window elements and setting geometry, the
    actual file handling is the responsibility of FileManager.

    Attributes:
        app: The main entry point into EasyQuant.
        scroll_list_box: The window element that contains the list of files.
        message_bar: Displays messages at the top of the window.
    """
    def __init__(self, app):
        self.app = app

        # Initialize the frame
        tk.Frame.__init__(self, app, background="white") # TODO: Use same init style as App.
        self.pack(fill=tk.BOTH, expand=1)

        # Initialize the list box and passes through the file_manager.
        self.scroll_list_box = scroll_list_box.ScrollListBox(self, self.app.file_manager)

        # Add import button
        self.add_button('Import', self.scroll_list_box.import_files)

        # Add message bar
        self.message_bar = message_bar.MessageBar(self)

        # Pack non-button elements in window
        self.pack_bottom(self.scroll_list_box)
        self.pack_bottom(self.message_bar)

    def add_button(self, text: str, command: Callable) -> None:
        button = tk.Button(self, text=text, command=command)
        self.pack_bottom(button)

    def pack_bottom(self, tk_object) -> None:
        tk_object.pack(side=tk.BOTTOM, fill=tk.BOTH)

    def set_message(self, message:str) -> None:
        self.message_bar.set_message(message)







