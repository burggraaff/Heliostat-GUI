"""
Module containing classes and functions to use for the heliostat GUIs.
"""

from __future__ import print_function, division

import Tkinter as tk
from Tkinter import *
from ttk import *
import tkMessageBox as messagebox

LABEL_FONT=('TkDefaultFont', 16)

import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

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
        self.means = np.array([])
        self.cross = (500, 500)

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
        if periodic:
            self.controller.after(1000, lambda: self.update(periodic = True))

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
            print("**** CONNECTING TO MOTOR ****")
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
            motor.table = np.loadtxt("static/{0}".format(serial_no))
            print(serial_no, "\n**** CONNECTED ****")
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
        image = self.led_image(self.cam)
        self.find_LEDs(image)
        self.plot_led_image(image)

        guess = self.initial_estimate()
        print("Moving to", guess)
        self.move_motors(*guess)
        # look up / calculate initial estimate for best position
        # optimise around that position

        # after alignment
        self.update()

    def move_motors(self, x, y, v=0.5):
        self.motor1.mcAbs(x, moveVel=v)
        self.motor2.mcAbs(y, moveVel=v)

    def initial_estimate(self):
        print(self.cross)
        indx = int(round(self.cross[0]/1280 * 9))
        indy = int(round(self.cross[1]/1024 * 9))
        print(indx, indy)
        posx = self.motor1.table[indx, indy]
        posy = self.motor2.table[indx, indy]
        return posx, posy

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
            embeddedInfo = cam.getEmbeddedImageInfo()
            if embeddedInfo.available.timestamp:
                cam.setEmbeddedImageInfo(timestamp = True)
            print("\n***** FINISHED CONNECTING TO FIBREHEAD LED CAMERA *****\n")
            return cam

    @staticmethod
    def led_image(camera, shutter=0.5, gain=12.0):
        if camera is None: #  checkerboard placeholder
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
        blur = cv2.GaussianBlur(image, (11,11), 0)  # blur to remove duplicates
        thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY)[1]
        data2,cnts,hie = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        means = np.array([x[0] for x in [np.mean(c, axis=0) for c in cnts]])
        if len(means) > 4:
            total_distances = [np.linalg.norm(x-means, axis=1).sum() for x in means]
            good = np.argsort(total_distances)[:4]
            means = means[good]
        means = means[means[:,1].argsort()] #  sort by y
        print("Found {0} contours".format(len(means)))
        print(means)
        return means

    def find_LEDs(self, image):
        self.means = self.find_sources(image)
        top = self.means[0]
        bottom = self.means[-1]
        self.cross = (top + bottom)/2.

    def plot_led_image(self, data):
        ax = self.fig.gca()
        ax.clear()
        ax.imshow(data)
        ax.axis("off")
        if len(self.means):
            vertx = [self.means[0][0], self.means[-1][0]]
            verty = [self.means[0][1], self.means[-1][1]]
            ax.plot(vertx, verty, c='r') # vertical
            if len(self.means) == 4:
                ax.plot(*self.means[1:3].T, c='r') # horizontal
        ax.scatter(*self.cross, c="r", s=35)
        self.fig.canvas.draw()