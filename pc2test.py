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

blur = cv2.GaussianBlur(data, (11,11), 0)
thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY)[1]
data2,cnts,hie = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print("Found {0} contours".format(len(cnts)))
means = np.array([x[0] for x in [np.mean(c, axis=0) for c in cnts]])
print(means)
tooclose = []
for j,m in enumerate(means):
    dists = np.linalg.norm(m-means[:j], axis=1)
    tooclose.extend(np.where((0 < dists) & (dists <= 15))[0])
means = np.delete(means, tooclose, axis=0)
print(means)
if len(cnts) > 4:
    total_distances = [np.linalg.norm(x-means, axis=1).sum() for x in means]
    print(total_distances)
    good = np.argsort(total_distances)[:4]
    means = means[good]
    print(means)
means = means[means[:,1].argsort()] #  sort by y

top = means[0]
bottom = means[-1]
cross = (top + bottom)/2.

plt.imshow(data)
for m in means:
    c = plt.Circle(m, 25, facecolor="none", edgecolor="red")
    plt.gca().add_artist(c)
plt.plot([top[0], bottom[0]], [top[1], bottom[1]], c="r")
plt.scatter(*cross)
plt.show()
