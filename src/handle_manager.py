#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 15:25:32 2024

@author: justin
"""

import numpy as np
from numpy.typing import NDArray
from typing import Optional
import matplotlib as mpl
from matplotlib import backend_bases
from src import curves

class HandleManager:
    def __init__(self, graph_manager, analysis_manager):
        """
        Takes care of selection and mapping of methods to of interactive
        handles on top of graphs/plots.

        graph_manager: a GraphManager object that the handles are located in.
        analysis_manager: The controller for the analysis.
        epsilon: Pick tolerance in pixels
        selected_handle: mpl Line2D object whose center is the picking target.
        selected_curve: the curve corresponding to the selected handle.
        clickpoint: the position of the click
        """
        self.graph_manager = graph_manager
        self.analysis_manager = analysis_manager

        self.epsilon: int = 7
        self.selected_handle: mpl.lines.Line2D = None
        self.selected_curve: curves.Curve = None
        self.clickpoint: NDArray = None

    def delete_gaussian(self, event: mpl.backend_bases.KeyEvent) -> None:
        if self.selected_curve is not None:
            # Do not remove baselines, which only have one parameter.
            if len(self.selected_curve.get_params()) != 1:
                self.analysis_manager.delete_gaussian(self.selected_curve)
                self.analysis_manager.update()


    def on_motion(self, event: backend_bases.KeyEvent) -> None:
        """
        Updates the fit when the handle is moved. If shift is held down, when
        moving the handle, it updates the height and width rather than the
        height and position.
        """
        if self.selected_handle is None or event.inaxes is None or event.button != 1:
            return

        key = event.key
        current_xy = np.array([event.xdata, event.ydata])
        curve = self.find_curve_by_handle(self.selected_handle)

        if curve is None:
            self.graph_manager.set_message("Error: No curve associated with "
                                           "the selected handle.")
            return

        if key == 'shift':
            self.analysis_manager.handle_moved_shift(curve, current_xy, self.clickpoint)
        else:
            self.analysis_manager.handle_moved(curve, current_xy)


    def on_button_press(self, event: mpl.backend_bases.KeyEvent) -> None:
        """
        Determines what to do upon click. Right click adds a default gaussian
        with the center and amplitude at the clickpoint. Left click selects
        and moves a handle.
        """
        self.graph_manager.canvas.get_tk_widget().focus_force()

        if event.button == 3:  # Right click adds a default gaussian.
            self.analysis_manager.add_gaussian(xc=event.xdata, A=event.ydata)
            return

        self.clickpoint = np.array([event.xdata, event.ydata])

        # Left click selects a handle.
        selected_handle = self.hit_test_handles(event)
        self.set_selected_handle(selected_handle)
        if self.selected_handle is None:
            return

        self.selected_curve = self.find_curve_by_handle(self.selected_handle)
        if self.selected_curve is None:
            self.graph_manager.set_message("Error: No curve associated with "
                                           "the selected handle.")


    def on_button_release(self, event: mpl.backend_bases.KeyEvent) -> None:
        """ passthrough function """
        self.graph_manager.on_key_release(event)



    def set_selected_handle(self, selected_handle: mpl.lines.Line2D) -> None:
        """
        Toggles the selection status of a handle object.
        selected_handle: The handle to be selected or deselected, if any
        Returns None
        """
        if selected_handle is not None:
            self._select_handle(selected_handle)
        else:
            self._deselect_current_handle()



    def _select_handle(self, handle: mpl.lines.Line2D) -> None:
        """
        Selects the specified handle.
        """
        if self.selected_handle is not None:
            self.graph_manager.mark_handle_as_deselected(self.selected_handle)

        self.selected_handle = handle
        self.graph_manager.mark_handle_as_selected(self.selected_handle)
        self.graph_manager.fig.canvas.draw()



    def _deselect_current_handle(self) -> None:
        """
        Deselects the currently selected handle, if any.
        """
        if self.selected_handle is not None:
            self.graph_manager.mark_handle_as_deselected(self.selected_handle)
            self.graph_manager.fig.canvas.draw()

        self.selected_handle = None


    def hit_test_handles(
            self,
            event: mpl.backend_bases.KeyEvent) -> Optional[mpl.lines.Line2D]:
        """
        Return closest handle within tolerance, otherwise None.
        """
        # The coordinates of the mouse click in pixels
        x, y = event.x, event.y

        handles = self.get_handles_with_valid_coordinates()
        if not handles:
            return None

        distances = self.calculate_distances_to_handles(handles, x, y)
        selected = self.find_closest_handle(handles, distances)
        return selected

    def get_handles_with_valid_coordinates(self) -> list[mpl.lines.Line2D]:
        """
        The second element of each curve_line value is the handle.
        """
        handles = [handle for _, handle in self.graph_manager.curve_lines.values()]
        return handles

    def find_curve_by_handle(
            self,
            handle: mpl.lines.Line2D) -> Optional[curves.Curve]:
        """Reverse lookup to find the curve associated with a given handle."""
        for curve, (line, hdl) in self.graph_manager.curve_lines.items():
            if hdl == handle:
                return curve
        return None

    def calculate_distances_to_handles(
            self,
            handles: list[mpl.lines.Line2D],
            x: int,
            y: int) -> NDArray:
        """
        x and y are the query coordinates in pixels.
        """
        distances = np.zeros(len(handles))
        for i, handle in enumerate(handles):
            gx, gy = self.get_display_coordinates(handle)
            distances[i] = np.hypot(x - gx, y - gy)
        return distances


    def find_closest_handle(
            self,
            handles: list[mpl.lines.Line2D],
            distances: NDArray) -> mpl.lines.Line2D:
        """
        handles is a list of handle objects and distances is a list of the
        calculated distances to the corresponding handles, in pixels.
        """
        min_distance_index = np.argmin(distances)
        if distances[min_distance_index] > self.epsilon:
            selected_handle = None
        else:
            selected_handle = handles[min_distance_index]
        return selected_handle


    def get_display_coordinates(self, handle: mpl.lines.Line2D) -> NDArray:
        """
        Gets the handle coordinates and transforms them into pixel values.
        """
        gx = handle.get_xdata()[0]
        gy = handle.get_ydata()[0]
        return self.graph_manager.fig.gca().transData.transform((gx, gy))