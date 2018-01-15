"""
Module containing classes and functions to use for the heliostat GUIs.
"""

from __future__ import print_function, division

import sys
pyversion = sys.version_info[0]

if pyversion == 2:
    import Tkinter as tk
    from Tkinter import *
    from ttk import *
    import tkFont as font
    import tkMessageBox
    
    from urllib import urlretrieve

elif pyversion == 3:
    import tkinter as tk
    from tkinter import *
    from tkinter.ttk import *
    from tkinter import font
    from tkinter import messagebox as tkMessageBox
    
    from urllib.request import urlretrieve
    
else:
    print("Sorry, this module is only available for Python versions 2 and 3. You are using Python {0}".format(pyversion))

LABEL_FONT=('TkDefaultFont', 16)

import numpy as np

import matplotlib.image as mpimg
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from astropy import coordinates as coord, units as u
from astropy.io import fits

from PIL import Image, ImageOps, ImageFont, ImageDraw, ImageTk

from .PyAPT import APTMotor

import PyCapture2 as pc2

def align_fibre():
    print("Align fibre")
    
class Align(tk.Frame):
    """
    Object that aids in aligning the fibre
    """
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialises Align object
        
        Parameters
        ----------
        self: self
        
        parent: parent frame, to draw this one in
        """
        self.parent = parent
        self.controller = controller
        tk.Frame.__init__(self, self.parent, *args, **kwargs)
        self.x = 0.
        self.y = 0.
        
        self.button = tk.Button(self, text = "ALIGN FIBRE", font = LABEL_FONT, height = 2, width = 10, command = self.align)
        self.button.grid(row = 0, column = 0, rowspan = 2, sticky = "news")
        self.labelx = tk.Label(self, text = "X:", font = LABEL_FONT)
        self.labelx.grid(row = 0, column = 1, sticky = "news", padx=5)
        self.labely = tk.Label(self, text = "Y:", font = LABEL_FONT)
        self.labely.grid(row = 1, column = 1, sticky = "news", padx=5)
        
        self.f = "{0:+.4f}" # format to print values in
        self.indicator_x = tk.Label(self, text = self.f.format(self.x), font = LABEL_FONT)
        self.indicator_x.grid(row = 0, column = 2, sticky = "e")
        self.indicator_y = tk.Label(self, text = self.f.format(self.y), font = LABEL_FONT)
        self.indicator_y.grid(row = 1, column = 2, sticky = "e")
        
        self.update(periodic = True)
        
    def update(self, periodic = False):
        self.x += 0.0098 # replace this with fetching the actual values
        self.y -= 0.9846 # replace this with fetching the actual values
        self.indicator_x["text"] = self.f.format(self.x)
        self.indicator_y["text"] = self.f.format(self.y)
        if periodic:
            self.controller.after(3*1000, lambda: self.update(periodic = True))
        
    def align(self):
        align_fibre()
        self.x = 0.
        self.y = 0.
        self.update()
