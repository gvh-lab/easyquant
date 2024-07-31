#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyQuant is a GUI-based program for fitting multiple, overlapping gaussian
curves to 2D data. It is mainly used to extract integrated intensities (i.e.,
areas under the curve) from SDS-PAGE gel profiles extracted by imageJ's 'plot
profile' tool.


Originally written by Rickard Hedman ca. ~2012 for the von Heijne lab, it was
later refactored by, and is still maintained by, Justin Westerfield of the same
group. It is a new version of the same software mentioned in (among others):
    - https://doi.org/10.7554/eLife.25642
    - https://doi.org/10.1073/pnas.2205810119
    - https://elifesciences.org/articles/36326
    - https://doi.org/10.1038/nsmb.2376
    - https://doi.org/10.1002/1873-3468.14562
    - https://doi.org/10.7554/eLife.64302


USAGE:
    This script is the main entry point into EasyQuant. Run this script to
    open the GUI.

TODO: Find the source of the segmentation fault. Occurs occasionally when
      running easyquant multiple times without restarting the kernel.
      Fault occurs when trying to open a file.

TODO: Fixed Gaussian widths are not maintained during fit optimization.
      This could probably be implemented with by modifying optimize_fit when
      called by analysis_manager.

TODO: (in scroll_list_box.py) Want to open files with a single click, but
      binding '<1>' to open_from_event fails because it calls the method before
      anything is selected. '<<ListboxSelect>>' works, but it makes the
      file_manager_window remain on top after opening the
      analysis_manager_window for some reason. Also, it doesn't change the
      active file after the analysis manager window is already open.
"""

import tkinter as tk
from src import analysis_manager
from src import file_manager_window
from src import file_manager

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Easy Quant")
        self.geometry("200x370")

        # Create file manager
        self.file_manager = file_manager.FileManager(self)

        # Initialize file manager window
        self.file_manager_window = file_manager_window.FileManagerWindow(self)

        # Initialize analysis manager
        self.analysis_manager = None

        # Protocol to carry out upon window closing
        self.protocol("WM_DELETE_WINDOW", self.close_program)


    def init_analysis_manager(self):
        if self.analysis_manager is None:
            self.analysis_manager = analysis_manager.AnalysisManager(self.file_manager, self)

    def update_analysis_manager(self):
        if self.analysis_manager is None:
            self.init_analysis_manager()
        self.analysis_manager.update()

    def close_program(self):
        self.destroy()


def main():
    app = App()
    app.mainloop()

if __name__ == '__main__':
    main()