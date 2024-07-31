#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 19:28:59 2024

@author: justin
"""

import tkinter as tk
from typing import Callable

class CreateToolTip(object):
    """
    Creates a tooltip for a given widget
    https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
    tk_ToolTip_class101.py
    gives a Tkinter widget a tooltip as the mouse is above the widget
    tested with Python27 and Python34  by  vegaseat  09sep2014
    www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter

    Modified to include a delay time by Victor Zaccardo, 25mar16

    Attributes:
        waittime: wait time in milliseconds.
        wraplength: Max length of tooltip in pixels.
        widget: The tk.Button object that hovering over creates a tooltip for.
        text: The text to appear in the tooltip.
        id: The integer identifier of the scheduled callback for tkinter.
        tw: The tk.Toplevel window that is created to house the tooltip.
    """
    def __init__(self, widget: tk.Button, text: str = 'widget info'):
        self.waittime: int = 500
        self.wraplength: int = 180
        self.widget: Callable[[], None] = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id: int = None
        self.tw: tk.Toplevel = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        tip_id = self.id
        self.id = None
        if tip_id:
            self.widget.after_cancel(tip_id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)

        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#ffffff", foreground='#000000',
                         relief='solid', borderwidth=1,
                         wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()