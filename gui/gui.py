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

LARGE_FONT= ('TkDefaultFont', 14)
LABEL_FONT=('TkDefaultFont', 16)

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

def align_fibre():
    print("Align fibre")

class Controls(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        self.parent = parent
        self.controller = controller
        tk.Frame.__init__(self, self.parent, *args, **kwargs)
        self.align = Align(parent = self, controller = self.controller)
        self.sun = Sun(parent = self, controller = self.controller)
        self.align.grid(row = 0, column = 0, sticky = "news", pady = 10)
        self.sun.grid(row = 1, column = 0, sticky = "news", pady = 10)

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

class Sun(tk.Frame):
    """
    Object that aids in displaying the orientation of the Sun
    """
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialises Sun object
        
        Parameters
        ----------
        parent: parent frame, to draw this one in
        """
        self.parent = parent
        self.controller = controller
        tk.Frame.__init__(self, self.parent, *args, **kwargs)
        
        self.button = tk.Button(self, text="UPDATE SUN", font = LABEL_FONT, command = self.plot) # button to update sun
        self.button.grid(row = 0, column = 0, sticky = "ew")
        self.fig = plt.figure(figsize=(6, 6), facecolor = "none")
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=1, column=0)
        self.plot() # initialise sun
    
    def plot(self):
        plot_sun(self.fig)
        self.controller.after(10*60*1000, self.plot) # automatically update every 10 mins

def sun_satellite(saveto = "sun.jpg"):
    url = "http://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg"
    urlretrieve(url, saveto)
    
def load_sun(dynamic = "sun.jpg", static = "static_images/sun_static.jpg"):
    try:
        sun_satellite(dynamic)
        img = Image.open(dynamic)
        print("Loaded live image of Sun from {0}".format(dynamic))
    except:
        img = Image.open(static)
        tkMessageBox.showwarning("Warning", "Unable to download live image of the Sun; using static one instead.")
        print("Loaded static image of Sun from {0}".format(static))
    
    return img

def rotation_angle(day = day_of_year):
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
    top=Image.open('static_images/Overlay.jpg')
    r,g,b=top.split()
    mask=Image.merge('L', (b,)) # to only copy text
    img.paste(top, (0,0), mask)
    img_projected = ImageOps.flip(img) # image is mirrored N/S by mirrors in heliostat
    img_projected = ImageOps.mirror(img_projected) # image is mirrored E/W by mirrors in heliostat
    img_rotated = img_projected.rotate(-angle)
    return img_rotated

def plot_sun(fig):
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

class Spectrum(tk.Frame):
    """
    Object that aids in displaying a spectrum
    """
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialises Spectrum object
        """
        self.parent = parent
        self.controller = controller
        tk.Frame.__init__(self, self.parent, *args, **kwargs)
        
        self.filename = "N/A"
        
        self.button = tk.Button(self, text = "TAKE SPECTRUM", font = LABEL_FONT, height = 2, width = 3, command = self.new_spectrum)
        self.button.grid(row = 0, column = 0, columnspan = 2, padx = 5, pady = 10, sticky = "news")
        self.label_integration = tk.Label(self, text = "INTEGRATION TIME", height = 2, width = 16, font = LABEL_FONT)
        self.label_integration.grid(row = 1, column = 0, sticky = "w")
        self.time = tk.Entry(self, font = LABEL_FONT)
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
        tkMessageBox.showerror("Error", "Exposure time \"{0}\" cannot be converted to floating point number".format(exposure_time))
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

def img(lang):
    return PhotoImage(Image.open("static_images/{0}.png".format(lang))).zoom(5).subsample(60)

class Page(tk.Frame): # individual page within interface
    def __init__(self, parent, controller, langfile, previous = None, nextpage = None, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.parent = parent
        self.controller = controller
        self.langfile = langfile
        self.translatables = []
        
        self.quit_button = tk.Button(self, text = "X", font = LARGE_FONT, height = 2, width = 5, bg = "red", command = lambda: quit(self.controller))
        self.quit_button.grid(row = 0, column = 5000, padx = 2.5, pady = 2.5, sticky = tk.NE) # column = 5000 ensures it is always on the far right
        
        if previous is not None:
            self.previous_button = tk.Button(self, text = "PREV", font = LARGE_FONT, height = 2, width = 5, command = lambda: self.controller.show_frame(previous))
            self.previous_button.grid(row = 1000, column = 0, padx = 2.5, pady = 2.5, sticky = "news")
        if nextpage is not None:
            self.next_button = tk.Button(self, text = "NEXT", font = LARGE_FONT, height = 2, width = 5, command = lambda: self.controller.show_frame(nextpage))
            self.next_button.grid(row = 1000, column = 5000, padx = 2.5, pady = 2.5, sticky = "news")

        
    def translate(self, lang):
        with open("{0}/{1}".format(self.langfile, lang)) as f:
            lines = f.readlines()
        for t, l in zip(self.translatables, lines):
            t["text"] = l
        self.flag_img_image = Image.open("static_images//{0}.png".format(lang)).resize((80, 55))
        self.flag_img = ImageTk.PhotoImage(self.flag_img_image)
        try:
            self.flag_button.destroy()
        except AttributeError:
            pass
        self.flag_button = tk.Button(self, image = self.flag_img, height = 55, width = 80, command = self.controller.translate_all)
        self.flag_button.grid(row = 0, column = 0, padx=2.5, pady=2.5)        

    def show(self):
        self.lift()

class Root(Tk): # main object, controls the programme
    def __init__(self, pages, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.is_fullscreen = False
        self.toggle_fullscreen()
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.end_fullscreen)
        
        self.language = "en"
        
        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky=tk.NSEW)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.geom = "1600x900+0+0"
        
        self.frames = {}
        
        print("Loading pages...")
        for p in pages:
            frame = p(container, self)
            self.frames[p] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        print("...Finished loading pages")
        
        self.translate_all()
        
        self.show_frame(pages[0])
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def translate_all(self):
        self.language = "nl" if self.language == "en" else "en" # switch between NL and EN
        for frame in self.frames.values():
            frame.translate(self.language)
        print("Translated all pages to {0}".format(self.language))
    
    def toggle_fullscreen(self, event = None):
        self.is_fullscreen = not self.is_fullscreen
        print("Toggled fullscreen {0}".format("on" if self.is_fullscreen else "off"))
        self.attributes("-fullscreen", self.is_fullscreen)
        if not self.is_fullscreen:
            self.wm_geometry(self.geom)
    
    def end_fullscreen(self, event = None):
        self.is_fullscreen = False
        print("Ended fullscreen")
        self.attributes("-fullscreen", False)
        self.wm_geometry(self.geom)

def quit(root):
    root.quit()
    root.destroy()
    print("Quit GUI")
