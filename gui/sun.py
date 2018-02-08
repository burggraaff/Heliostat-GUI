"""
Frame that contains the image of the Sun in its current orientation.
"""

from __future__ import print_function, division

from Tkinter import Frame, Button
import tkFont as font
import tkMessageBox as messagebox
from urllib import urlretrieve

LARGE_FONT = ('TkDefaultFont', 16)

import numpy as np
import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from PIL import Image, ImageOps

day_of_year = datetime.datetime.now().timetuple().tm_yday

class Sun(Frame):
    """
    Frame that displays the orientation of the Sun.
    """
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialises Sun object

        Parameters
        ----------
        parent: parent frame, to draw this one in
        controller: controller object that handles timing calls
        """
        self.parent = parent
        self.controller = controller
        Frame.__init__(self, self.parent, *args, **kwargs)

        self.button = Button(self, text="UPDATE SUN", font = LARGE_FONT, command = self.plot) # button to update sun
        self.button.grid(row = 0, column = 0, sticky = "ew")
        self.fig = plt.figure(figsize=(4, 4), facecolor = "none")
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=1, column=0)
        self.plot() # initialise sun

    def plot(self):
        """
        Draw and periodically update the figure showing the Solar orientation.

        The figure is automatically updated every 10 minutes - N.B. manual
        calls to this function will create additional automatic updates.
        """
        plot_sun(self.fig)
        self.controller.after(10*60*1000, self.plot) # automatically update every 10 mins

def sun_satellite(saveto = "sun.jpg"):
    """
    Fetch a live satellite image of the Sun from NASA.

    Parameters
    ----------
    saveto: Location to save the image to.
    """
    url = "http://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg"
    urlretrieve(url, saveto)

def load_sun(dynamic = "sun.jpg", static = "static/sun_static.jpg"):
    """
    Load an image of the Sun. First try to download a live image; if this is
    not possible, use a pre-loaded static image.

    Parameters
    ----------
    dynamic: Location to save/load live image to/from.
    static: Location to load static image from.

    Returns
    -------
    img: PIL Image object containing image of the Sun.
    """
    try:
        sun_satellite(dynamic)
        img = Image.open(dynamic)
        print("Loaded live image of Sun from {0}".format(dynamic))
    except:
        img = Image.open(static)
        messagebox.showwarning("Warning", "Unable to download live image of the Sun; using static one instead.")
        print("Loaded static image of Sun from {0}".format(static))

    return img

def rotation_angle(day = day_of_year):
    """
    Calculate the angle of rotation of the Sun from N-S orientation due to
    its rotation on the sky and the effects of the heliostat.

    Parameters
    ----------
    day: Current day of the year (integer)

    Returns
    -------
    rotation_angle: The angle of rotation.
    """
    # the image on the screen is rotated 24 degrees from perpendicular (to the right when looking towards the screen)
    rotation_angle = 24.
    #now we calculate the effect from the orientation of the Earth's axis relative to its orbit
    #this varies between -23.43707 and +23.43707 degrees during the year as a sine wave
    #0 at the summer solstice (21 June) and at the winter solstice (21 December)

    #x=np.arange(0,365.25,0.25) How Pim does it - he doesn't remember why steps of 0.25
    #y=[23.43707*np.sin(2*np.pi*(i*360.0/365.0 - 172*360.0/365.0)) for i in x] #in degrees
    #extra_angle=y[day_of_year]

    earth_axis = 23.43707
    offset = 172. # 21 june is the 172nd day of the year
    extra_angle = earth_axis * np.sin(2. * np.pi * (day - offset) / 365.)

    #now we calculate the effect of the rotation of the Earth during the day
    now = datetime.datetime.now()
    today = now.date()
    noon = datetime.time(hour = 12)
    noon_today = datetime.datetime.combine(today, noon)
    diff = now - noon_today
    hours = diff.total_seconds()/3600.
    degrees = hours * 15.
    rotation_angle = rotation_angle - degrees - extra_angle
    return rotation_angle

def sun_rotate(img, angle):
    """
    Rotate an image of the Sun with the current rotation as would be seen on
    the screen at the heliostat.
    Also overlays NSEW indicators on the image.

    Parameters
    ----------
    img: Image of the Sun to rotate.
    angle: Angle by which to rotate.

    Returns
    -------
    img_rotated: The rotated image.
    """
    top=Image.open('static/Overlay.jpg')
    r,g,b=top.split()
    mask=Image.merge('L', (b,)) # to only copy text
    img.paste(top, (0,0), mask)
    img_projected = ImageOps.flip(img) # image is mirrored N/S by mirrors in heliostat
    img_projected = ImageOps.mirror(img_projected) # image is mirrored E/W by mirrors in heliostat
    img_rotated = img_projected.rotate(-angle)
    return img_rotated

def plot_sun(fig):
    """
    Plot an image of the Sun into a given figure, including rotation and a
    line for the equator.

    Parameters
    ----------
    fig: matplotlib figure to draw into.
    """
    img = load_sun()
    angle = rotation_angle()
    print("Rotation angle of the sun: {0:.2f}".format(angle))
    angle_rad = np.radians(angle)
    img_rotated = sun_rotate(img, angle)

    centerx = centery = 512
    x = 512. * np.cos(angle_rad)
    y = 512. * np.sin(angle_rad)

    ax = fig.gca()
    ax.clear()
    ax.plot([centerx - x, centerx + x], [centery - y, centery + y], c='k', lw=5, ls="--")
    ax.imshow(img_rotated)

    ax.set_xlim(0, 1024)
    ax.set_ylim(0, 1024)
    ax.invert_yaxis()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    fig.tight_layout(True)
    fig.canvas.draw()
