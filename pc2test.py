"""
Testing PyCapture2
"""
from __future__ import print_function
import PyCapture2 as pc2
print("Imported pc2")
from matplotlib import pyplot as plt
import cv2
import numpy as np

def printCameraInfo(cam):
    camInfo = cam.getCameraInfo()
    print("\n*** CAMERA INFORMATION ***")
    print("Serial number - ", camInfo.serialNumber)
    print("Camera model - ", camInfo.modelName)
    print("Camera vendor - ", camInfo.vendorName)
    print("Sensor - ", camInfo.sensorInfo)
    print("Resolution - ", camInfo.sensorResolution)
    print("Firmware version - ", camInfo.firmwareVersion)
    print("Firmware build time - ", camInfo.firmwareBuildTime)

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


def ledimage(cam, shutter = 0.5, gain = 12.0):
    cam.setProperty(type = pc2.PROPERTY_TYPE.SHUTTER, absControl=True, autoManualMode=False, absValue = 0.5)
    cam.setProperty(type = pc2.PROPERTY_TYPE.GAIN, absControl=True, autoManualMode=False, absValue = 12.0)
    cam.startCapture()
    image = cam.retrieveBuffer()
    cam.stopCapture()

    data = np.array(image.getData())  # np.array() call prevents crash
    shape = (image.getRows(), image.getCols())
    data = data.reshape(shape)

    return data

bus = pc2.BusManager()
numCams = bus.getNumOfCameras()
print("Number of cameras detected:", numCams)

cam = pc2.Camera()
cam.connect(bus.getCameraFromIndex(0))
printCameraInfo(cam)

fmt7info, supported = cam.getFormat7Info(0)
fmt7imgSet = pc2.Format7ImageSettings(0, 0, 0, fmt7info.maxWidth, fmt7info.maxHeight, pc2.PIXEL_FORMAT.MONO8)
fmt7pktInf, isValid = cam.validateFormat7Settings(fmt7imgSet)
cam.setFormat7ConfigurationPacket(fmt7pktInf.recommendedBytesPerPacket, fmt7imgSet)

d = pc2.PROPERTY_TYPE.__dict__
props = [key for key in d.keys() if isinstance(d[key], int)]

enableEmbeddedTimeStamp(cam, True)
cam.setProperty(type = pc2.PROPERTY_TYPE.SHUTTER, absControl=True, autoManualMode=False, absValue = 0.5)
cam.setProperty(type = pc2.PROPERTY_TYPE.GAIN, absControl=True, autoManualMode=False, absValue = 12.0)
cam.startCapture()
image = grabImages(cam, 1)
cam.stopCapture()

data = image.getData()
shape = (image.getRows(), image.getCols())
data = data.reshape(shape)

print(data.min(), data.max())

plt.imshow(data)
plt.show()