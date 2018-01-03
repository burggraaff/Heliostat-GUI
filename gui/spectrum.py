"""
Module containing classes and functions to use for the heliostat GUIs.
"""

from __future__ import print_function, division

from sys import version_info
pyversion = version_info[0]

if pyversion == 2:
    from Tkinter import Frame, Button, Label, Entry
    import tkFont as font
    import tkMessageBox as messagebox
    
elif pyversion == 3:
    from tkinter import Frame, Button, Label, Entry, font, messagebox
        
else:
    print("Sorry, this module is only available for Python versions 2 and 3. You are using Python {0}".format(pyversion))

LARGE_FONT = ('TkDefaultFont', 16)

import numpy as np
import ephem
import datetime

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


#import Fitting_script as fs

day_of_year = datetime.datetime.now().timetuple().tm_yday

def timestamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

class Spectrum(Frame):
    """
    Object that aids in displaying a spectrum
    """
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialises Spectrum object
        """
        self.parent = parent
        self.controller = controller
        Frame.__init__(self, self.parent, *args, **kwargs)
        
        self.filename = "N/A"
        
        self.button = Button(self, text = "TAKE SPECTRUM", font = LARGE_FONT, height = 2, width = 3, command = self.new_spectrum)
        self.button.grid(row = 0, column = 0, columnspan = 2, padx = 5, pady = 10, sticky = "news")
        self.label_integration = Label(self, text = "INTEGRATION TIME", height = 2, width = 16, font = LARGE_FONT)
        self.label_integration.grid(row = 1, column = 0, sticky = "w")
        self.time = Entry(self, font = LARGE_FONT)
        self.time.insert(0, 10)
        self.time.grid(row = 1, column = 1, sticky = "w")

        self.fig, axs = plt.subplots(nrows = 2, sharex = True, figsize = (8, 5), tight_layout = True, facecolor = "none")
        self.ax_e, self.ax_s = axs
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan = 2, sticky='news')
        
    def new_spectrum(self):
        self.expose()
        self.read_data()
        self.plot()
        
    def expose(self):
        self.filename = expose(self.time.get())
    
    def read_data(self):
        self.data = reduce_spectrum(self.filename)
        
    def plot(self):
        plot_spectrum(self.data, self.fig, self.ax_e, self.ax_s, title = self.filename + ".fit")

def expose(exposure_time):
    try:
        time = float(exposure_time)
    except:
        messagebox.showerror("Error", "Exposure time \"{0}\" cannot be converted to floating point number".format(exposure_time))
        raise ValueError("Exposure time \"{0}\" cannot be converted to floating point number".format(exposure_time))
    print("Exposing for {0} seconds".format(time))
    # ACTUAL EXPOSURE TO BE ADDED HERE
    filename = timestamp() + ".fit"
    return "examples/Mooi"

def reduce_spectrum(filename):
    raw_data = fits.getdata(filename + ".fit").astype(np.int16)
    dark_data = fits.getdata(filename + "_DarkCurrent.fit").astype(np.int16)
    data = raw_data - dark_data
    data = data.T
    return data

def plot_spectrum(data, fig, a_exp, a_spec, title = ""):
    a_exp.clear()
    a_exp.imshow(data[225:475], origin = "upper")
    a_exp.get_xaxis().set_visible(False)
    a_exp.get_yaxis().set_visible(False)
    a_exp.set_title(title)
    
    a_spec.clear()
    collapsed = data.sum(axis=0)
    a_spec.plot(collapsed)
    a_spec.axis("tight")
    
    a_spec.set_xlim(0, len(data))
        
    fig.canvas.draw()
