#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 15:09:40 2024

@author: justin

"""

import tkinter as tk

class MessageBar(tk.Text):
    def __init__(self, container):
        tk.Text.__init__(self, container, height=1)

        default_message = "Welcome to EasyQuant!"

        self.configure(state=tk.DISABLED)
        self.set_message(default_message)

    def set_message(self, message_text: str):
        '''
        Adds a message to the text box
        '''
        self['state'] = 'normal'
        self.delete(1.0, 'end')
        self.insert("1.end", message_text)
        self['state'] = 'disabled'