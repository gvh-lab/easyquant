#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 21:07:37 2024

@author: justin
"""

import os
import csv
import numpy as np
from numpy.typing import NDArray
from src import curves

class QuantData():
    """
    A QuantData object contains information such as the file path and
    contents. Could also be named File, DataFile, Profile, RawData, etc.

    Attributes:
        path: The full file path to the data file.
        base: The file name with the extension. e.g., data.txt
        name: The file name without the extension. e.g., data
        x: The list of x values from the file as an np.ndarray
        y: same as x but for y values.
        composite_curve: The Curve object that will hold the fits to the data.
    """

    def __init__(self, path):
        self.path = path
        self.base = os.path.basename(path)
        self.name = os.path.splitext(self.base)[0]

        self.x, self.y = read_csv(path)

        self.composite_curve: curves.Curve = None

def read_csv(path: str) -> tuple[NDArray]:
    """
    Reads a csv file based on a path. Skips headers.

    Returns
        x, y (np.arrays): Values from the first and second columns of the file.
    """
    with open(path, 'r') as csvfile:

        first_characters = csvfile.read(1024) # First 1024 chars
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(first_characters)
        has_headers = sniffer.has_header(first_characters)

        csvfile.seek(0) # Start from beginning of file.
        reader = csv.reader(csvfile, dialect)
        if has_headers:
            next(reader) # Skip first row. Deals with ImageJ headers.

        data = np.array(list(reader), dtype=float)
        x, y = data[:, 0], data[:, 1]
        return x, y

