#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 00:27:54 2024

@author: justin
"""

import tkinter as tk
from src import graph_manager
from src import file_toolbar
from src import message_bar

class AnalysisWindow(tk.Toplevel):
    """
    This represents the window itself. Initiates window elements, whereas
    communication between elements is handled by AnalysisManager. Also handles
    window closing events.

    Attributes:
        analysis_manager: The overall controller for the analysis.
        graph_manager: The graph frame within the window.
        message_bar: Displays messages underneath the graph.
        info_box: Displays information on plotted curves.
        file_toolbar: Toolbar that handles switching between files.
    """
    def __init__(self, analysis_manager):
        super().__init__()
        self.analysis_manager = analysis_manager

        # Initialize window elements
        self.graph_manager = graph_manager.GraphManager(self, self.analysis_manager) # Used to pass in qd here. outsourcing to manager.
        self.message_bar = message_bar.MessageBar(self)
        self.info_box = InfoBox(self)
        self.file_toolbar = file_toolbar.FileToolbar(self, self.analysis_manager.file_manager, self.analysis_manager)

        self.setup_layout()

        # Handle window closing event.
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_layout(self):
        # Set up grid to expand w/ window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Grid window elements (more flexible than pack)
        self.graph_manager.grid(row=0, column=0, sticky="ew", padx=5, pady=5, columnspan=2)
        self.info_box.grid(row=1, column=0, sticky="ew", padx=5, pady=5, columnspan=2)
        self.message_bar.grid(row=2, column=0, sticky="ew", padx=5, pady=5, columnspan=2)
        self.file_toolbar.grid(row=3, column=0, sticky="ew", padx=5, pady=5, columnspan=2)

    def on_closing(self):
        self.analysis_manager.app.analysis_manager = None
        self.destroy()



class InfoBox(tk.Text):
    """
    A text box that displays information such as fitting parameters.
    """
    def __init__(self, analysis_window):
        tk.Text.__init__(self, analysis_window)

        self.config(state='disabled', height=6)

    def set_info(self, content:str) -> None:
        """ Accesses and updates the info box. """
        self.config(state='normal')
        self.delete(1.0, tk.END)
        self.insert(tk.END, content)
        self.config(state='disabled')