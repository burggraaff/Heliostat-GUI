"""
Frame that contains the spectrum as measured by the SBIG camera.
"""

from __future__ import print_function, division

from SBIG.speccamera import Camera

from Tkinter import Frame, Button, Label, Entry
import tkFont as font
import tkMessageBox as messagebox

LARGE_FONT = ('TkDefaultFont', 16)

import numpy as np
import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from astropy.io import fits

def timestamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

class Spectrum(Frame):
    """
    Frame that displays the spectrum.
    """
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialises Spectrum object.

        Parameters
        ----------
        parent: parent frame, to draw this one in
        controller: controller object that handles timing calls
        """
        self.parent = parent
        self.controller = controller
        Frame.__init__(self, self.parent, *args, **kwargs)

        print("***** CONNECTING TO SPECTRAL (SBIG) CAMERA *****")
        try:
            self.camera = Camera()
        except:  # to allow GUI use without spectral camera
            self.camera = None
            print("***** COULD NOT CONNECT *****")
        else:
            print("***** CONNECTED *****")

        self.filename = "N/A"

        self.button = Button(self, text = "TAKE SPECTRUM", font = LARGE_FONT, height = 2, width = 3, command = self.new_spectrum)
        self.button.grid(row = 0, column = 0, columnspan = 2, padx = 5, pady = 10, sticky = "news")
        self.label_integration = Label(self, text = "INTEGRATION TIME", height = 2, width = 16, font = LARGE_FONT)
        self.label_integration.grid(row = 1, column = 0, sticky = "w")
        self.time = Entry(self, font = LARGE_FONT)
        self.time.insert(0, 5)
        self.time.grid(row = 1, column = 1, sticky = "w")

        self.fig, axs = plt.subplots(nrows = 2, sharex = True, figsize = (8, 5), tight_layout = True, facecolor = "none")
        self.ax_e, self.ax_s = axs
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan = 2, sticky='news')

    def new_spectrum(self):
        """
        Record and plot a new spectrum
        """
        self.expose()
        self.read_data()
        self.plot()

    def expose(self):
        """
        Fetch exposure time from the input field and take an image.
        """
        if self.camera is None:  # test mode -- immediately return test image
            print("NO SPECTRAL CAMERA FOUND -- USING TEST DATA")
            self.filename = "example_fits_files/Mooi"
            return

        exposure_time = self.time.get()
        try:
            self.exposure_time = float(exposure_time)
        except:
            message = "Exposure time \"{0}\" cannot be converted to floating point number".format(exposure_time)
            messagebox.showerror("Error", message)
            raise ValueError(message)
        filename = "spectra/{0}".format(timestamp())
        self.camera.spectrum(self.exposure_time, filename)
        self.filename = filename

    def read_data(self):
        """
        Read spectral data from the current filename.
        """
        self.data = reduce_spectrum(self.filename)

    def plot(self):
        """
        Plot the currnetly loaded spectrum.
        """
        plot_spectrum(self.data, self.fig, self.ax_e, self.ax_s, title = "Solar spectrum")
        
    def intensity(self):
        return np.percentile(self.data[225:475], 98) / self.exposure_time

def reduce_spectrum(filename):
    raw_data = fits.getdata(filename + ".fit").astype(np.int16)
    dark_data = fits.getdata(filename + "_DarkCurrent.fit").astype(np.int16)
    data = raw_data - dark_data
    data = data.T
    return data

def plot_spectrum(data, fig, a_exp, a_spec, title = ""):
    a_exp.clear()
    a_exp.imshow(data[225:], origin = "upper", vmin = np.percentile(data.ravel(), 2), vmax = np.percentile(data.ravel(), 98))
    a_exp.get_xaxis().set_visible(False)
    a_exp.get_yaxis().set_visible(False)
    a_exp.set_title(title)

    a_spec.clear()
    collapsed = data.sum(axis=0)
    a_spec.plot(collapsed)
    a_spec.axis("tight")

    a_spec.set_xlim(0, len(data))

    fig.canvas.draw()
