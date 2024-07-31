#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 14:37:50 2024

@author: justin
"""

import tkinter as tk
from typing import Optional
from src import quant_data

class FileManager:
    """
    Keeps track of files and their quant data objects.

    Attributes:
        app: Main entry point into EasyQuant program.
        qd_list: List of all QuantData objects. Same indices as in listbox.
        active_index: index of the currently active QuantData object in list.
    """
    def __init__(self, app):
        self.app = app
        self.qd_list = []
        self.active_index: Optional[int] = None



    def set_active_index(self, index: Optional[int] = None) -> None:
        self.active_index = index
        self.app.update_analysis_manager()



    def get_active_qd(self) -> Optional[quant_data.QuantData]:
        if self.active_index is not None:
            qd = self.qd_list[self.active_index]
            return qd
        else:
            return None



    def import_files(self) -> None:
        """
        Uses tk module to get paths for user-selected files.
        Registers each file name in the qd_list.
        """
        for filename in tk.filedialog.askopenfilenames():
            self.register_file(filename)



    def register_file(self, filename: str) -> None:
        """
        Inits a quantdata object for a file and adds it to the qd_list.
        """
        qd = quant_data.QuantData(filename)
        self.qd_list.append(qd)



    def prev_file(self) -> None:
        if self.active_index > 0:
            self.active_index -= 1



    def next_file(self) -> None:
        max_index = len(self.qd_list) - 1
        if self.active_index < max_index:
            self.active_index += 1