#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 17:02:56 2024

@author: Justin
"""

import numpy as np
from typing import Union, Optional, Tuple, List
from numpy.typing import ArrayLike
from abc import ABC
from abc import abstractmethod


class Curve(ABC):
    """
    Abstract class defining everything that is a 'Curve' that can be fit
    (e.g., Gaussian). This probably wasn't necessary, but I guess it will be
    helpful if I want to add more Curves in the future.
    abstract methods must be redefined later.
    """
    @abstractmethod
    def get_params(self):
        ...

    @abstractmethod
    def set_params(self):
        ...

    @abstractmethod
    def evaluate(self):
        ...


class Constant(Curve):
    """
    A constant curve which makes the baseline.

    Attributes:
        y: Float that determines the vertical position of the function.
        xc: Used for sorting, i.e., denotes that this is a baseline for
            CompositeCurve and HandleManager.
    """
    def __init__(self, constant: float):
        self.y = constant
        self.xc = -1

    def clone(self) -> Curve:
        return Constant(self.y)



    def get_params(self) -> Tuple[float]:
        """
        Returns self.y in a singleton tuple, as the result must be iterable
        for the CompositeCurve's get_params method.
        """
        return tuple([self.y])



    def set_params(self, y: float = None) -> None:
        if y is not None:
            self.y = y



    def evaluate(
            self,
            x: Optional[Union[ArrayLike, float]] = None,
            *params: Tuple[float]) -> Optional[Union[ArrayLike, float]]:
        """
        If params are passed in (i.e., if they have been set by a fitting
        operation) it will use that value. If not, it will just take the value
        of self.y.

        Args:
            x: The value(s) at which to evaluate the curve.
            *params: Passed in by CompositeCurve upon composite evaluation.

        Returns:
        x+0+y: Returns y, or an array of y of same length as x. x*0 is just to
               show logic.
        """
        if x is None:
            return

        if len(params) > 0:
            y = params[0]
        else:
            y = self.y

        return x * 0 + y



    def area(self) -> int:
        return 0




class Gaussian(Curve):
    """
    An amplitude gaussian curve, where an amplitude gaussian is evaluated as
        GaussAmp = y0 + A*exp(-(x-xc)**2/(2*w**2))

    Attributes:
        xc: The center point of the gaussian on the x-axis (float). Also used
            for sorting.
        A: Amplitude of the gaussian (float).
        w: Width at half max of the gaussian (float).
    """
    def __init__(self, xc: float = 0, A: float = 1, w: float = 1):
        self.xc = abs(xc)
        self.A = abs(A)
        self.w = abs(w)

    def __del__(self):
        pass

    def clone(self) -> Curve:
        return Gaussian(self.xc, self.A, self.w)



    def get_params(self) -> Tuple[float]:
        return self.xc, self.A, self.w



    def set_params(self, xc:float = None, A:float = None, w:float = None) -> None:
        """
        Sets params (center, amplitude, or width), makes them
        positive values.
        """
        if xc is not None:
            self.xc = abs(xc)
        if A is not None:
            self.A = abs(A)
        if w is not None:
            self.w = abs(w)



    def evaluate(
            self,
            x: Optional[Union[ArrayLike, float]] = None,
            *params: Tuple[float]) -> Optional[Union[ArrayLike, float]]:
        """
        Returns height of gaussian curve at position(s) x.  If params are
        passed in, it will use those. Otherwise it will use pre-defined
        attributes.
        """
        if x is None:
            return

        if len(params) > 0:
            xc = params[0]
            A = params[1]
            w = params[2]

        else:
            xc = self.xc
            A = self.A
            w = self.w

        return A*np.exp( -0.5*((x-xc)/w)**2 )



    def area(self) -> float:
        """ Returns area under the gaussian. """
        sqrtPIdiv2 = np.sqrt(np.pi/2)
        return 2 * self.A * self.w * sqrtPIdiv2




class CompositeCurve(Curve):
    """
    A composite curve made up of several "subcurves". Evaluated like a
    compound expression.

    Attributes:
        curve_list: A list of Curve objects.
    """
    def __init__(self):
        self.curve_list = []

    def clone(self) -> Curve:
        composite_curve = CompositeCurve()
        for curve in self.curve_list:
            composite_curve.curve_list.append(curve.clone())
        return composite_curve



    def get_params(self) -> List[float]:
        """
        Returns a long list of parameters, not delimited but for their length
        in the corresponding curve. I.e., if you know the curve_list is sorted,
        and you know how long the params are of each curve, you can determine
        which params go to which curve. Embraces a bit of chaos.
        """
        params = []
        for curve in self.curve_list:
            params.extend(curve.get_params())
        return params



    def set_params(self, *params: List[float]) -> None:
        """
        Sets the params for each curve in curve_list. Determines which curve
        to set params for based on the knowledge that curve_list is sorted, and
        that each curve has a set length of params.
        """
        i = 0
        for curve in self.curve_list:
            param_length = len(curve.get_params())
            curve.set_params(*params[i:i+param_length])
            i += param_length



    def evaluate(
            self,
            x: Optional[Union[ArrayLike, float]] = None,
            *params: Tuple[float]) -> Optional[Union[ArrayLike, float]]:
        """
        Returns height of the composite cuve at position(s) x. Goes through
        and evaluates each curve in curve_list individually (either with new
        params or existing ones) and sums the result.
        """

        if x is None:
            return

        y = 0

        # If new parameters are present, evaluate the the curve with those.
        if params:
            i = 0
            for curve in self.curve_list:
                param_length = len(curve.get_params())
                y += curve.evaluate(x, *params[i:i+param_length])
                i += param_length

        # Evaluate the curve with the current parameters.
        else:
            for curve in self.curve_list:
                y += curve.evaluate(x)

        return y



    def sort(self) -> None:
        """
        Sorts the list of curves, self.curve_list, based on their centers, xc.
        """
        self.curve_list = sorted(self.curve_list, key=lambda curve: curve.xc)
