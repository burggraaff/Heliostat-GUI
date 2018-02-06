"""
Module containing classes and functions to use for the heliostat GUIs.
"""

from __future__ import print_function, division

import Tkinter as tk
LABEL_FONT=('TkDefaultFont', 16)

import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import cv2

try:
    from PyAPT import APTMotor
except ImportError:
    use_motors = False
else:
    use_motors = True

serial_no_1 = 26000369
serial_no_2 = 26000370
dll_location = r"gui\APT.dll"

try:
    import PyCapture2 as pc2
except ImportError:
    use_camera = False
else:
    use_camera = True

class Aligner(object):
    """
    Object that handles the alignment of the fibre, including controlling
    the motors and talking to the fibrehead LED camera.
    """
    def __init__(self, serial_1 = serial_no_1, serial_2 = serial_no_2):
        """
        Initialise Aligner object. Looks for Thorlabs motors with given
        serial numbers, and for any PointGrey camera.
        Note: maybe use serial number for PG camera as well?
        
        Parameters
        ----------
        serial_1: int
            Serial number of first Thorlabs motor
        serial_2: int
            Serial number of second Thorlabs motor
        """
        self.camera = self.connect_camera()
        self.motor1 = self.connect_motor(serial_1)
        self.motor2 = self.connect_motor(serial_2)

        self.led_coords = np.array([])
        self.fibre_coords = (-1, -1)

    def end(self):
        """
        Disconnect motors and camera to prevent issues when re-starting.
        """
        self.motor1.cleanUpAPT()
        self.motor2.cleanUpAPT()
        self.camera.disconnect()

    def get_current_positions(self):
        return self.motor1.getPos(), self.motor2.getPos()

    @staticmethod
    def connect_motor(serial_no):
        print("**** CONNECTING TO MOTOR ****")
        try:
            motor = APTMotor(SerialNum = serial_no, dllname=dll_location)
        except Exception as e:
            print(e)
        try:
            motor.go_home()
        except ValueError:
            pass  # always gives a ValueError for some reason
        motor.identify()  # blink to show connection clearly
        motor.table = np.loadtxt("static/{0}.txt".format(serial_no))
        print(serial_no, "\n**** CONNECTED ****")
        return motor

    @staticmethod
    def connect_camera():
        print("\n***** CONNECTING TO FIBREHEAD LED CAMERA *****")
        bus = pc2.BusManager()
        numCams = bus.getNumOfCameras()
        assert numCams, "\n***** COULD NOT CONNECT TO FIBREHEAD LED CAMERA ******\n"
        camera = Camera(bus)
        print("\n***** FINISHED CONNECTING TO FIBREHEAD LED CAMERA *****\n")
        return camera

    def move_motors(self, x, y, v=0.5):
        print("Moving to ({0}, {1})".format(x,y))
        self.motor1.mcAbs(x, moveVel=v)
        self.motor2.mcAbs(y, moveVel=v)

    @staticmethod
    def find_sources(image):
        blur = cv2.GaussianBlur(image, (11,11), 0)  # blur to remove duplicates
        thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY)[1]
        data2,cnts,hie = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        means = np.array([x[0] for x in [np.mean(c, axis=0) for c in cnts]])
        if len(means) > 4:  # find cluster of four close sources
            total_distances = [np.linalg.norm(x-means, axis=1).sum() for x in means]
            good = np.argsort(total_distances)[:4]
            means = means[good]
        means = means[means[:,1].argsort()] #  sort by y
        print("Found {0} contours".format(len(means)))
        print(means)
        return means

    def find_LEDs(self, image):
        self.led_coords = self.find_sources(image)
        top = self.led_coords[0]
        bottom = self.led_coords[-1]
        self.fibre_coords = (top + bottom)/2.

    def initial_estimate(self):
        print("Fibre at", self.fibre_coords)
        indx = int(round(self.fibre_coords[0]/1280 * 9))
        indy = int(round(self.fibre_coords[1]/1024 * 9))
        print("Indices", indx, indy)
        posx = self.motor1.table[indx, indy]
        posy = self.motor2.table[indx, indy]
        return posx, posy

    def align(self):
        # use camera to find fibre for inistial estimate
        image = self.camera.led_image()
        self.find_LEDs(image)  # fibre position now in self.fibre_coords

        # look up / calculate initial estimate for best position
        guess = self.initial_estimate()
        self.move_motors(*guess)
        # optimise around that position

        return image, self.led_coords, self.fibre_coords


class Camera(pc2.Camera):
    """
    PointGrey Camera object.
    """
    def __init__(self, bus, index=0):
        pc2.Camera.__init__(self)
        self.connect(bus.getCameraFromIndex(index))
        self.printCameraInfo()
        embeddedInfo = self.getEmbeddedImageInfo()
        if embeddedInfo.available.timestamp:
            self.setEmbeddedImageInfo(timestamp=True)

    def printCameraInfo(self):
        camInfo = self.getCameraInfo()
        print("CAMERA INFORMATION")
        print("Serial number - ", camInfo.serialNumber)
        print("Camera model - ", camInfo.modelName)
        print("Camera vendor - ", camInfo.vendorName)
        print("Sensor - ", camInfo.sensorInfo)
        print("Resolution - ", camInfo.sensorResolution)
        print("Firmware version - ", camInfo.firmwareVersion)
        print("Firmware build time - ", camInfo.firmwareBuildTime)

    def led_image(self, shutter=0.5, gain=12.0):
        self.setProperty(type=pc2.PROPERTY_TYPE.SHUTTER, absControl=True, autoManualMode=False, absValue=shutter)
        self.setProperty(type=pc2.PROPERTY_TYPE.GAIN, absControl=True, autoManualMode=False, absValue=gain)
        self.startCapture()
        image = self.retrieveBuffer()
        self.stopCapture()
        imgdata = np.array(image.getData())  # np.array() call prevents crash
        shape = (image.getRows(), image.getCols())
        imgdata = imgdata.reshape(shape)
        return imgdata


class AlignFrame(tk.Frame):
    """
    Frame that displays the alignment of the fibre.
    """
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialises AlignFrame object

        Parameters
        ----------
        parent: parent frame, to draw this one in
        controller: controller object that handles timing calls
        """
        self.parent = parent
        self.controller = controller
        tk.Frame.__init__(self, self.parent, *args, **kwargs)
        self.x = self.y = -9999.9999

        try:
            self.aligner = Aligner()
        except:
            self.aligner = None

        self.button = tk.Button(self, text = "ALIGN FIBRE", font = LABEL_FONT, height = 2, width = 10, command = self.align)
        self.button.grid(row = 0, column = 0, columnspan=2, sticky = "news")

        self.fig = plt.figure(figsize=(4, 4), facecolor = "none")
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan=2)

        self.f = "{0}: {1:+.4f}" # format to print values in
        self.indicator_x = tk.Label(self, text = self.f.format("X", self.x), font = LABEL_FONT)
        self.indicator_x.grid(row = 1, column = 1, sticky = "w")
        self.indicator_y = tk.Label(self, text = self.f.format("Y", self.y), font = LABEL_FONT)
        self.indicator_y.grid(row = 2, column = 1, sticky = "w")

        self.update(periodic = True)

    def end(self):
        if self.aligner is not None:
            self.aligner.end()

    def update(self, periodic = False):
        if self.aligner is not None:
            self.x, self.y = self.aligner.get_current_positions()
        self.indicator_x["text"] = self.f.format("X", self.x)
        self.indicator_y["text"] = self.f.format("Y", self.y)
        if periodic:
            self.controller.after(1000, lambda: self.update(periodic = True))

    def align(self):
        try:
            image, leds, fibre = self.aligner.align()
        except Exception as e:  # placeholder if photo cannot be used
            image = np.kron([[1, 0] * 4, [0, 1] * 4] * 4, np.ones((10,10)))
            leds = fibre = np.array([])
        self.plot_led_image(image, leds, fibre)

    def plot_led_image(self, image, leds=np.array([]), fibre=np.array([])):
        ax = self.fig.gca()
        ax.clear()
        ax.imshow(image)
        ax.axis("off")
        if len(leds):
            vertx = [leds[0][0], leds[-1][0]]
            verty = [leds[0][1], leds[-1][1]]
            ax.plot(vertx, verty, c='r') # vertical
            if len(leds) == 4:
                ax.plot(*leds[1:3].T, c='r') # horizontal
        if len(fibre):
            ax.scatter(*fibre, c="r", s=35)
        self.fig.canvas.draw()