#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 10:59:42 2024

@author: Justin

This module contains functions used for fitting curves to data.
"""

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import optimize, signal
from src import curves


def optimize_fit(
        x: ArrayLike,
        y: ArrayLike,
        initial_curve: curves.Curve) -> curves.Curve:
    """
    Takes data, and a model with initial parameters and optimizes the fit.
    Returns the fitted curve. Works with any Curve type which has clone,
    evaluate, get_params and set_params methods. x and y must have same length.
    """
    popt, pcov = optimize.curve_fit(initial_curve.evaluate, x, y, p0=initial_curve.get_params())

    fitted_curve = initial_curve.clone()
    fitted_curve.set_params(*popt)

    return fitted_curve

def estimate_fit(x: ArrayLike,
                 y: ArrayLike) -> curves.CompositeCurve:
    """
    Estimates a CompositeCurve fit from data. Smoothes data with a Savitzky-
    Golay filter, then uses derivatives to find peaks. Baseline is estimated
    from y data, and a gaussian is assigned to each peak.

    # TODO: Estimate noise and adjust the smoothing accordingly
    """

    # Smooth the data
    y = signal.savgol_filter(y, window_length=21, polyorder=4)

    h = (x[1]-x[0]) # X range as a tuple for some reason.

    # Calculate the 1st and 2nd derivatives
    dy = compute_numerical_derivative(y, h, 1)
    ddy = compute_numerical_derivative(dy, h, 1)

    estimated_fit = curves.CompositeCurve()

    # Baseline estimate is the first point's y coordinate.
    estimated_fit.curve_list.append(curves.Constant(y[0]))

    # Estimate peak locations, amplitudes and widths

    # Find points where the first derivative crosses zero
    zero_crossing_indices = find_zero_crossings(dy)

    vertical_range_of_data = (y.max()-y[0])
    acceptable_peak_height = 0.5 * vertical_range_of_data

    for i in zero_crossing_indices:
        # If the 2nd dervative is negative it could be a peak
        if ddy[i] < 0:
            w_est = np.sqrt(-y[i] / ddy[i])
            peak_height = (y[i]-y[0])

            if w_est < 3 and peak_height > acceptable_peak_height:
                new_gaussian = curves.Gaussian(xc=x[i], A=y[i]-y[0], w=w_est)
                estimated_fit.curve_list.append(new_gaussian)

    return estimated_fit

def compute_numerical_derivative(
        y: ArrayLike,
        step_size: float = 1.0,
        num_iterations: int = 1) -> NDArray[float]:
    """
    Compute the numerical derivative of a given array using the three-point
    finite difference method.

    Parameters:
    - y (numpy.ndarray): The input array for which the derivative is
        to be computed.
    - step_size (float): The step size used in the finite difference method.
        Default is 1.0.
    - num_iterations (int): The number of iterations to apply the finite
        difference method. Default is 1.

    Returns:
    - numpy.ndarray: The array containing the computed numerical derivative.
    """
    for iteration in range(num_iterations):
        # Compute the three-point finite difference
        derivative_values = (y[2:] - y[:-2]) / (2.0 * float(step_size))

        # Pad values at the extremes to keep the size constant
        derivative_values = np.concatenate(([derivative_values[0]], derivative_values, [derivative_values[-1]]))

    return derivative_values


def find_zero_crossings(y: ArrayLike) -> NDArray[float]:
    """
    Find zero-crossings in a given array.

    Parameters:
    - y (numpy.ndarray): The input array for which zero-crossings
        are to be identified.

    Returns:
    - numpy.ndarray: An array containing the indices of zero-crossings in the
        input array.
    """
    zero_crossings = np.where(np.diff(np.sign(y)))[0]
    return zero_crossings

