"""
Testing PyCapture2
"""
from __future__ import print_function
import PyCapture2 as pc2
print("Imported pc2")
from matplotlib import pyplot as plt
import cv2

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

bus = pc2.BusManager()
numCams = bus.getNumOfCameras()
print("Number of cameras detected:", numCams)

cam = pc2.Camera()
cam.connect(bus.getCameraFromIndex(0))
printCameraInfo(cam)

enableEmbeddedTimeStamp(cam, True)
cam.startCapture()
image = grabImages(cam, 1)
cam.stopCapture()

data = image.getData()
shape = (image.getRows(), image.getCols())
print(shape)
data = data.reshape(shape)

plt.imshow(data)
plt.show()