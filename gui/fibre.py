"""
Module containing classes and functions to use for the heliostat GUIs.
"""

from __future__ import print_function, division

import Tkinter as tk
from Tkinter import *
from ttk import *
import tkFont as font
import tkMessageBox as messagebox

from urllib import urlretrieve

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
serial_no_1 = 26000369
serial_no_2 = 26000370

import PyCapture2 as pc2


def align_fibre():
    print("Align fibre")

def printCameraInfo(cam):
    camInfo = cam.getCameraInfo()
    print("CAMERA INFORMATION")
    print("Serial number - ", camInfo.serialNumber)
    print("Camera model - ", camInfo.modelName)
    print("Camera vendor - ", camInfo.vendorName)
    print("Sensor - ", camInfo.sensorInfo)
    print("Resolution - ", camInfo.sensorResolution)
    print("Firmware version - ", camInfo.firmwareVersion)
    print("Firmware build time - ", camInfo.firmwareBuildTime)
    print("")


def enableEmbeddedTimeStamp(cam, enableTimeStamp):
    embeddedInfo = cam.getEmbeddedImageInfo()
    if embeddedInfo.available.timestamp:
        cam.setEmbeddedImageInfo(timestamp = enableTimeStamp)
        if(enableTimeStamp):
            print("\nTimeStamp is enabled.\n")
        else:
            print("\nTimeStamp is disabled.\n")


def grabImages(cam, numImagesToGrab):
    prevts = None
    for i in range(numImagesToGrab):
        try:
            image = cam.retrieveBuffer()
        except pc2.Fc2error as fc2Err:
            print("Error retrieving buffer : ", fc2Err)
            continue

        ts = image.getTimeStamp()
        if(prevts):
            diff = (ts.cycleSeconds - prevts.cycleSeconds) * 8000 + (ts.cycleCount - prevts.cycleCount)
            print("Timestamp [", ts.cycleSeconds, ts.cycleCount, "] -", diff)
        prevts = ts

    print("Saving the last image to LED_photo.png")
    image.save("LED_photo.png", pc2.IMAGE_FILE_FORMAT.PNG)
    return image


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
        self.x = self.y = -1000

        self.cam = self.connect_camera()
        self.motor1 = self.connect_motor(serial_no_1)
        self.motor2 = self.connect_motor(serial_no_2)

        self.button = tk.Button(self, text = "ALIGN FIBRE", font = LABEL_FONT, height = 2, width = 10, command = self.align)
        self.button.grid(row = 0, column = 0, rowspan = 2, sticky = "news")
        self.labelx = tk.Label(self, text = "X:", font = LABEL_FONT)
        self.labelx.grid(row = 0, column = 1, sticky = "news", padx=5)
        self.labely = tk.Label(self, text = "Y:", font = LABEL_FONT)
        self.labely.grid(row = 1, column = 1, sticky = "news", padx=5)

        self.fig = plt.figure(figsize=(4, 4), facecolor = "none")
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=100, column=0)

        self.f = "{0:+.4f}" # format to print values in
        self.indicator_x = tk.Label(self, text = self.f.format(self.x), font = LABEL_FONT)
        self.indicator_x.grid(row = 0, column = 2, sticky = "e")
        self.indicator_y = tk.Label(self, text = self.f.format(self.y), font = LABEL_FONT)
        self.indicator_y.grid(row = 1, column = 2, sticky = "e")

        self.update(periodic = True)

    def update(self, periodic = False):
        if self.motor1 is not None:
            self.x = self.motor1.getPos()
        if self.motor2 is not None:
            self.y = self.motor2.getPos()
        self.indicator_x["text"] = self.f.format(self.x)
        self.indicator_y["text"] = self.f.format(self.y)
        if periodic:
            self.controller.after(3*1000, lambda: self.update(periodic = True))

    def end(self):
        if self.cam is not None:
            self.cam.disconnect()
        if self.motor1 is not None:
            self.motor1.cleanUpAPT()
        if self.motor2 is not None:
            self.motor2.cleanUpAPT()

    @staticmethod
    def connect_motor(serial_no):
        try:
            motor = APTMotor(SerialNum = serial_no)
        except:
            print("Could not connect to motor with Serial number {0}".format(serial_no))
            return None
        try:
            motor.go_home()
        except ValueError:
            pass  # always gives a ValueError for some reason
        motor.identify()
        return motor

    def align(self):
        if self.cam is None:
            messagebox.showwarning("Warning", "No fibrehead LED camera found")
            raise ValueError("No fibrehead LED camera found")
        if self.motor1 is None or self.motor2 is None:
            messagebox.showwarning("Warning", "(one of) the motor controllers not found")
            raise ValueError("One of the motor controllers not found")
        self.led_image()
        align_fibre()
        self.motor1.go_home()
        self.motor2.go_home()
        self.update()

    @staticmethod
    def connect_camera():
        print("\n***** CONNECTING TO FIBREHEAD LED CAMERA*****")
        bus = pc2.BusManager()
        numCams = bus.getNumOfCameras()
        if numCams == 0:
            print("\n***** COULD NOT CONNECT TO FIBREHEAD LED CAMERA ******\n")
            return None
        else:
            cam = pc2.Camera()
            cam.connect(bus.getCameraFromIndex(0))
            printCameraInfo(cam)
            enableEmbeddedTimeStamp(cam, True)
            print("\n***** FINISHED CONNECTING TO FIBREHEAD LED CAMERA *****\n")
            return cam

    def led_image(self):
        self.img = grabImages(self.cam, 1)
        shape = (self.img.getRows(), self.img.getCols())
        self.imgdata = self.img.getData().reshape(shape)
        self.fig.imshow(self.imgdata)