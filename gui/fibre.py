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

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from astropy import coordinates as coord, units as u
from astropy.io import fits

from PIL import Image, ImageOps, ImageFont, ImageDraw, ImageTk

import cv2

try:
    from .PyAPT import APTMotor
except ImportError:
    use_motors = False
else:
    use_motors = True

serial_no_1 = 26000369
serial_no_2 = 26000370

try:
    import PyCapture2 as pc2
except ImportError:
    use_camera = False
else:
    use_camera = True


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
            print("TimeStamp is enabled.")
        else:
            print("TimeStamp is disabled.")


def grabImages(cam, numImagesToGrab):
    prevts = None
    cam.startCapture()
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

    cam.stopCapture()
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
        self.x = self.y = -9999.9999

        global use_camera ; global use_motors
        self.cam = self.connect_camera(use_camera)
        self.camera_warning_given = False
        self.motor1 = self.connect_motor(serial_no_1, use_motors)
        self.motor2 = self.connect_motor(serial_no_2, use_motors)
        self.motor_warning_given = False

        self.button = tk.Button(self, text = "ALIGN FIBRE", font = LABEL_FONT, height = 2, width = 10, command = self.align)
        self.button.grid(row = 0, column = 0, columnspan=2, sticky = "news")

        self.fig = plt.figure(figsize=(4, 4), facecolor = "none")
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan=2)
        self.circles = []

        self.f = "{0}: {1:+.4f}" # format to print values in
        self.indicator_x = tk.Label(self, text = self.f.format("X", self.x), font = LABEL_FONT)
        self.indicator_x.grid(row = 1, column = 1, sticky = "w")
        self.indicator_y = tk.Label(self, text = self.f.format("Y", self.y), font = LABEL_FONT)
        self.indicator_y.grid(row = 2, column = 1, sticky = "w")

        self.update(periodic = True)

    def update(self, periodic = False):
        if self.motor1 is not None:
            self.x = self.motor1.getPos()
        if self.motor2 is not None:
            self.y = self.motor2.getPos()
        self.indicator_x["text"] = self.f.format("X", self.x)
        self.indicator_y["text"] = self.f.format("Y", self.y)
        self.plot_led_image(self.led_image(self.cam))
        if periodic:
            self.controller.after(1250, lambda: self.update(periodic = True))

    def end(self):
        if self.cam is not None:
            self.cam.disconnect()
        if self.motor1 is not None:
            self.motor1.cleanUpAPT()
        if self.motor2 is not None:
            self.motor2.cleanUpAPT()

    @staticmethod
    def connect_motor(serial_no, use_motors = True):
        if not use_motors:
            return None
        else:
            try:
                motor = APTMotor(SerialNum = serial_no)
            except:
                print("Could not connect to motor with Serial number {0}".format(serial_no))
                return None
            try:
                motor.go_home()
            except ValueError:
                pass  # always gives a ValueError for some reason
            motor.identify()  # blink to show connection clearly
            return motor

    def align(self):
        if self.cam is None and not self.camera_warning_given:
            messagebox.showwarning("Warning", "No fibrehead LED camera found")
            self.camera_warning_given = True
            raise ValueError("No fibrehead LED camera found")
        if (self.motor1 is None or self.motor2 is None) and not self.motor_warning_given:
            messagebox.showwarning("Warning", "(one of the) Motor controllers not found")
            self.motor_warning_given = True
            raise ValueError("One of the motor controllers not found")
        self.plot_led_image(self.led_image(self.cam))
        align_fibre()
        # TEMPORARY:
        self.motor1.identify()
        self.motor2.identify()

        self.update()

    @staticmethod
    def connect_camera(use_camera):
        if not use_camera:
            return None
        print("\n***** CONNECTING TO FIBREHEAD LED CAMERA *****")
        bus = pc2.BusManager()
        numCams = bus.getNumOfCameras()
        if numCams == 0:
            print("\n***** COULD NOT CONNECT TO FIBREHEAD LED CAMERA ******\n")
            use_camera = False
            return None
        else:
            cam = pc2.Camera()
            cam.connect(bus.getCameraFromIndex(0))
            printCameraInfo(cam)
            enableEmbeddedTimeStamp(cam, True)
            print("\n***** FINISHED CONNECTING TO FIBREHEAD LED CAMERA *****\n")
            return cam

    @staticmethod
    def led_image(camera, shutter=0.5, gain=12.0):
        if camera is None:
            imgdata = np.kron([[1, 0] * 4, [0, 1] * 4] * 4, np.ones((10,10)))
        else:
            camera.setProperty(type=pc2.PROPERTY_TYPE.SHUTTER, absControl=True, autoManualMode=False, absValue=shutter)
            camera.setProperty(type=pc2.PROPERTY_TYPE.GAIN, absControl=True, autoManualMode=False, absValue=gain)
            camera.startCapture()
            image = camera.retrieveBuffer()
            camera.stopCapture()

            imgdata = np.array(image.getData())  # np.array() call prevents crash
            shape = (image.getRows(), image.getCols())
            imgdata = imgdata.reshape(shape)

        return imgdata

    @staticmethod
    def find_sources(image):
        thresh = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)[1]
        data2,cnts,hie = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        print("Found {0} contours".format(len(cnts)))
        means = np.array([x[0] for x in [np.mean(c, axis=0) for c in cnts]])
        if len(cnts) > 4:
            total_distances = [np.linalg.norm(x-means, axis=1).sum() for x in means]
            good = np.argsort(total_distances)[:4]
            means = means[good]
        return means

    def plot_led_image(self, data):
        ax = self.fig.gca()
        ax.imshow(data)
        ax.axis("off")
        for c in self.circles:
            c.remove()
        means = self.find_sources(data)
        self.circles = [plt.Circle(m, 25, facecolor="none", edgecolor="red") for m in means]
        for c in self.circles:
            ax.add_artist(c)
        self.fig.canvas.draw()