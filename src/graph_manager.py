#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 21:17:25 2024

@author: justin

"""

import collections
import numpy as np
from typing import Optional, Deque, Dict
from numpy.typing import ArrayLike, NDArray
import tkinter as tk

import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src import curves
from src import graph_toolbar
from src import handle_manager

mpl.use('TkAgg')
mpl.rc('font', size='11.0', weight='light',
       **{'family':'sans-serif', 'sans-serif':['Arial']})
mpl.interactive(True)

class GraphManager(tk.Frame):
    """
    This class manages the window where the graph appears.
    In a MVC architecture, this class would represent a view element.

    Attributes:
        analysis_window: The window in which this frame is found.
        analysis_manager: The main controller for the analysis.
        fig: A matplotlib Figure object which contains the plot.
        axes: A matplotlib Axes object, which represents the (only) subplot.
        canvas: The interactive tkinter canvas on which the figure is drawn.
        handle_manager: A subclass which deals with interactive handles.
        x: The x-axis points. Same bounds as raw data, but more points.
        curve_lines: Dict of {curve: (line, handle)}
        data_line: The mpl.Line object for the raw data.
        composite_curve_line: The mpl.Line object for the composite curve.
        graph_toolbar: A class that handles the toolbar under the graph.
        history:
        redo_undo_counter: An int that keeps track of the position in history.
    """
    def __init__(self, analysis_window, analysis_manager):
        tk.Frame.__init__(self, analysis_window)

        self.analysis_window = analysis_window
        self.analysis_manager = analysis_manager

        # Add figure and subplot
        self.fig = Figure(figsize=(7,5), dpi=90)
        self.axes = self.fig.add_subplot(1, 1, 1)
        self.set_axes_labels()

        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH,
                                         expand=tk.YES)
        self.canvas.draw()

        # Event handler
        self.handle_manager = handle_manager.HandleManager(self,
                                                           analysis_manager)
        self.fig.canvas.mpl_connect('button_press_event',
                                    self.handle_manager.on_button_press)
        self.fig.canvas.mpl_connect('button_release_event',
                                    self.handle_manager.on_button_release)
        self.fig.canvas.mpl_connect('motion_notify_event',
                                    self.handle_manager.on_motion)

        # Connect events to methods.
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('key_release_event', self.on_key_release)

        self.x: Optional[NDArray] = None
        self.curve_lines: Dict = {}
        self.data_line: mpl.lines.Line2D = None
        self.composite_curve_line: mpl.lines.Line2D = None
        self.history: Optional[Deque] = None
        self.undo_redo_counter: int = 0

        # Custom toolbar.
        self.graph_toolbar = graph_toolbar.GraphToolbar(self.canvas, self,
                                                        self.analysis_manager)


    def active_qd_changed(self) -> None:
        """
        Sets the graph up to plot a new curve. Does not modify the
        CompositeCurve of the QuantData object. Typically called when changing
        files.
        """
        qd = self.analysis_manager.get_active_qd()
        self.axes.clear()
        self.curve_lines = {}
        self.set_axes_labels()
        self.set_x_from_qd()
        self.axes.set_title(qd.name)
        self.update_plot()
        self.init_history()

    def fit_changed(self) -> None:
        """ Updates the history and plot. """
        # Set the fitted curve into history
        qd = self.analysis_manager.get_active_qd()
        self.history.appendleft(qd.composite_curve.clone())

        # Replot the data
        self.update_plot()

# PLOTTING

    def update_plot(self) -> None:
        """
        Removes all lines and plots them again. self.fig must be defined.
        """
        for line in self.axes.lines:
            line.remove()

        qd = self.analysis_manager.get_active_qd()
        self.curve_lines = {}

        # Data line
        self.data_line = self.plot_data(qd.x, qd.y)

        # Baseline
        baseline_curve = qd.composite_curve.curve_list[0]
        self.add_curve(baseline_curve, color='green')

        # Individual curves and their handles
        if len(qd.composite_curve.curve_list) > 1:
            for curve in qd.composite_curve.curve_list[1:]:
                self.add_curve(curve)

        # Composite curve
        self.composite_curve_line = self.plot_curve(qd.composite_curve,
                                                    color='red', alpha=0.8)

        self.fig.canvas.draw()


    def set_axes_labels(self, xlabel:str="Distance (cm)",
                        ylabel:str="Gray value") -> None:
        self.axes.set_ylabel(ylabel)
        self.axes.set_xlabel(xlabel)


    def plot_data(self,
                  x: ArrayLike,
                  y: ArrayLike) -> mpl.lines.Line2D:
        """
        Plots data curves (i.e., not fitted curves). self.axes must be defined.
        Returns the line object to be able to refer to the line that was drawn.
        """
        pid, = self.axes.plot(x, y, linestyle='-', linewidth=1.5, color='k')
        return pid



    def add_curve(self, curve: curves.Curve, **options) -> None:
        """
        Plots a gaussian and its handle and adds it to the self.curve_lines
        dict. Passes **options to the line, not the handle. Curve needs to have
        an evaluate method.
        """
        line = self.plot_curve(curve, **options)
        handle = self.plot_handle(curve)
        self.curve_lines[curve] = (line, handle)



    def plot_handle(self, curve: curves.Curve) -> mpl.lines.Line2D:
        """
        Determines the midpoint of the gaussian, or, if it's a baseline, the
        plot. Plots the handle in self.axes and returns the handle (Line2D)
        """
        xc = self.get_curve_midpoint(curve)
        handle, = self.axes.plot(xc, curve.evaluate(xc), 'o', ms=10,
                                 alpha=0.4, color='yellow')
        return handle



    def plot_curve(self, curve: curves.Curve, **options) -> mpl.lines.Line2D:
        """
        Plots a curve in self.axes using its evaluate() method. **options are
        forwarded to the mpl.axes.plot() method.
        """
        line, = self.axes.plot(self.x, curve.evaluate(self.x), linestyle='-',
                               linewidth=1.5, **options)
        return line



    def get_curve_midpoint(self, curve: curves.Curve) -> float:
        """
        Checks whether the centerpoint positive and if so, returns the pre-
        defined centerpoint. Otherwise, returns the center of the plot.
        Curve objects of Constant type have xc = -1. Their midpoints
        therefore default to the center of the plot.
        """
        if curve.xc > 0:
            return curve.xc
        else:
            return calculate_x_midpoint(self.x)



    def update_line(self, curve: curves.Curve, draw: bool = True) -> None:
        """
        Takes a Curve object, checks the self.curve_lines dict for its
        corresponding line (mpl.lines.Line2D object), and updates it using the
        current params from the curve. 'draw' dictates whether to draw to the
        canvas. Reducing unecessary drawing improves interactive response time.
        """
        line = self.curve_lines[curve][0]
        line.set_data(self.x, curve.evaluate(self.x))
        if draw:
            self.fig.canvas.draw()

    def update_handle(self, curve: curves.Curve, draw: bool = True) -> None:
        """
        Takes a Curve object, checks the self.curve_lines dict for its
        corresponding handle (mpl.lines.Line2D object), and updates it using
        the current params from the curve. Determines the midpoint of the
        gaussian, or, if it's a baseline, the plot.'draw' dictates whether to
        draw to the canvas. Reducing unecessary drawing improves interactive
        response time.
        """
        xc = self.get_curve_midpoint(curve)
        handle = self.curve_lines[curve][1]
        handle.set_data(xc, curve.evaluate(xc))
        if draw:
            self.fig.canvas.draw()

    def update_composite_curve_line(self, draw: bool = True) -> None:
        """
        Updates the composite curve line (mpl.lines.Line2D object) using
        current params from the composite curve (CompositeCurve object).'draw'
        dictates whether to draw to the canvas. Reducing unecessary drawing
        improves interactive response time.
        """
        qd = self.analysis_manager.get_active_qd()
        y = qd.composite_curve.evaluate(self.x)
        self.composite_curve_line.set_data(self.x, y)
        if draw:
            self.fig.canvas.draw()

    def mark_handle_as_selected(self, handle: mpl.lines.Line2D) -> None:
        """
        handle (mpl.lines.Line2D): The handle to be recolored.
        Returns: None
        """
        handle.set_color("blue")

    def mark_handle_as_deselected(self, handle: mpl.lines.Line2D) -> None:
        """
        handle (mpl.lines.Line2D): The handle to be recolored.
        Returns: None
        """
        handle.set_color("yellow")


# EVENTS

    def on_key_press(self, event: mpl.backend_bases.KeyEvent) -> None:
        """
        Set keyboard Shortcuts by binding key presses to methods.

        Dependencies:
            self.handle_manager
            self.analysis_manager
            self.analysis_window
        """
        if event.key == 'backspace':
            self.handle_manager.delete_gaussian(event)

        if event.key == 'f':
            self.analysis_manager.optimize_fit()

        if event.key == 'e':
            self.analysis_manager.estimate_fit()

        if event.key == 'n':
            self.analysis_window.file_toolbar.next_file()

        if event.key == 'p':
            self.analysis_window.file_toolbar.prev_file()

        if event.key == 's':
            self.analysis_manager.export()

        if event.key == 'z':
            self.undo()

        if event.key == 'r':
            self.redo()



    def on_key_release(self, event: mpl.backend_bases.KeyEvent) -> None:
        """ Updates history if the composite curve changed. """
        qd = self.analysis_manager.get_active_qd()
        if qd.composite_curve.get_params() != self.history[0].get_params():
            self.history.appendleft(qd.composite_curve.clone())
            self.analysis_manager.set_message("Gaussian moved manually.")
            self.analysis_manager.update_gauss_table()


# HISTORY

    def init_history(self) -> None:
        """
        Initializes the history manager, self.history
        """
        qd = self.analysis_manager.get_active_qd()
        self.history = collections.deque([qd.composite_curve.clone()], 15)
        self.redo_undo_counter = 0


    def undo(self) -> None:
        """
        Takes the CompositeCurve from the hisotry deque's -1 position and sets
        a clone of that as the QuantData's current one. If it were to set the
        actual object from the history, any modification would propagate, and
        we don't want to rewrite history do we?
        """
        if self.history[-1] and self.redo_undo_counter > -len(self.history)+1:
            qd = self.analysis_manager.get_active_qd()
            self.history.rotate(-1)
            qd.composite_curve = self.history[0].clone()
            self.redo_undo_counter -= 1

            self.update_plot()
            self.analysis_manager.update_gauss_table()
            self.analysis_manager.set_message("Undid something")


    def redo(self) -> None:
        """
        Takes the CompositeCurve from the hisotry deque's +1 position and sets
        a clone of that as the QuantData's current one.
        """
        if self.history[1] and self.redo_undo_counter < 0:
            qd = self.analysis_manager.get_active_qd()
            self.history.rotate(1)
            qd.composite_curve = self.history[0].clone()
            self.redo_undo_counter += 1

            self.update_plot()
            self.analysis_manager.update_gauss_table()
            self.analysis_manager.set_message("Redid something.")

# INBOUND COMMUNICATION

    def set_x_from_qd(self, n_steps: int = 1000) -> None:
        """
        Generates a range of x values with bounds pulled from the QuantData
        object's x values (raw data). Sets the new array as self.x.
        """
        qd = self.analysis_manager.get_active_qd()
        xmin, xmax = qd.x[0], qd.x[-1]
        self.x = np.linspace(xmin, xmax, n_steps)

# HELPERS

def calculate_x_midpoint(x: ArrayLike) -> NDArray:
    """
    x is a sorted series of numbers for which to find the midpoint.
    """
    return np.array( [( x[0] + x[-1] ) / 2.0] )