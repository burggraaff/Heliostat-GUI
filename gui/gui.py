"""
Module containing classes and functions to use for the heliostat GUIs.
"""

from __future__ import print_function, division

from sys import version_info
assert version_info[0] == 2 and version_info[1] == 7,\
     "This GUI is only compatible with Python 2.7.x"

from .fibre import Align
from .sun import Sun
from .spectrum import Spectrum

import Tkinter as tk
from Tkinter import *
from ttk import *
import tkFont as font
import tkMessageBox

from urllib import urlretrieve

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

day_of_year = datetime.datetime.now().timetuple().tm_yday

class Controls(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        self.parent = parent
        self.controller = controller
        tk.Frame.__init__(self, self.parent, *args, **kwargs)
        self.align = Align(parent = self, controller = self.controller)
        self.sun = Sun(parent = self, controller = self.controller)
        self.align.grid(row = 0, column = 0, sticky = "news", pady = 10)
        self.sun.grid(row = 1, column = 0, sticky = "news", pady = 10)

def img(lang):
    return Image.open("localisation/flags/{0}.png".format(lang)).resize((80, 55))

class Page(tk.Frame): # individual page within interface
    def __init__(self, parent, controller, langfile, previous = None, nextpage = None, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.parent = parent
        self.controller = controller
        self.langfile = langfile
        self.translatables = []

        self.quit_button = tk.Button(self, text = "X", font = LARGE_FONT, height = 2, width = 5, bg = "red", command = self.end)
        self.quit_button.grid(row = 0, column = 5000, padx = 2.5, pady = 2.5, sticky = tk.NE) # column = 5000 ensures it is always on the far right

        if previous is not None:
            self.previous_button = tk.Button(self, text = "PREV", font = LARGE_FONT, height = 2, width = 5, command = lambda: self.controller.show_frame(previous))
            self.previous_button.grid(row = 1000, column = 0, padx = 2.5, pady = 2.5, sticky = "news")
        if nextpage is not None:
            self.next_button = tk.Button(self, text = "NEXT", font = LARGE_FONT, height = 2, width = 5, command = lambda: self.controller.show_frame(nextpage))
            self.next_button.grid(row = 1000, column = 5000, padx = 2.5, pady = 2.5, sticky = "news")

    def translate(self, lang):
        with open("localisation/{0}/{1}".format(self.langfile, lang)) as f:
            lines = f.readlines()
        for t, l in zip(self.translatables, lines):
            t["text"] = l
        self.flag_img_image = Image.open("localisation/flags/{0}.png".format(lang)).resize((80, 55))
        self.flag_img = ImageTk.PhotoImage(self.flag_img_image)
        try:
            self.flag_button.destroy()
        except AttributeError:
            pass
        self.flag_button = tk.Button(self, image = self.flag_img, height = 55, width = 80, command = self.controller.translate_all)
        self.flag_button.grid(row = 0, column = 0, padx=2.5, pady=2.5)

    def show(self):
        self.lift()

    def end(self):
        end(self.controller)


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

def end(GUI):
    GUI.quit()
    GUI.destroy()
    print("Quit GUI")
