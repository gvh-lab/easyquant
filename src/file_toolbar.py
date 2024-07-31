#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 14:49:19 2024

@author: justin
"""

import tkinter as tk

class FileToolbar(tk.Frame):
    """
    This toolbar contains file navigation commands. It therefore acts as an
    interface between the file manager and the analysis manager.

    Attributes:
        file_manager: The object that contains the list of files.
        analysis_manager: The main controller for the analysis.
    """
    def __init__(self, container, file_manager, analysis_manager):
        """
        Container is required to initialize tk.Frame inside another window.
        In this case, it's the analysis window.
        """
        tk.Frame.__init__(self, container)
        self.file_manager = file_manager
        self.analysis_manager = analysis_manager

        self.add_button("Previous file", self.prev_file)
        self.add_button("Next file", self.next_file)

    def pack_left(self, tk_object):
        tk_object.pack(side='left')

    def add_button(self, text, command):
        button = tk.Button(self, text=text, command=command)
        self.pack_left(button)

    def next_file(self):
        self.file_manager.next_file()
        self.analysis_manager.update()

    def prev_file(self):
        self.file_manager.prev_file()
        self.analysis_manager.update()