from __future__ import print_function, division
import time
import numpy
from astropy.io import fits

import Sbigudrv as sbig

# N.B. CAPITAL CODES are mostly just integers
# some magic numbers should be replaced with codes for clarity

def check_output(output, msg_good="", msg_bad="Failure!"):
    if output == sbig.CE_NO_ERROR:
        print(msg_good)
    else:
        raise ValueError(msg_bad + "\nError code: {0}".format(output))


def status(command):
    qcsp = sbig.QueryCommandStatusParams()
    qcsr = sbig.QueryCommandStatusResults()
    qcsp.command = command
    err = sbig.SBIGUnivDrvCommand(sbig.CC_QUERY_COMMAND_STATUS, qcsp, qcsr)
    return qcsr.status


class Camera(object):
    def __init__(self, working_temperature=0.0):
        self.working_temperature = working_temperature
        self.startup()

    def startup(self):
        self._open_driver()
        self._open_device()
        self._establish_link()
        self._set_temperature(self.working_temperature, cool=True)
        self._activate_fan()
        while self._query_temperature[2] > self.working_temperature:
            #  wait for camera to cool down
            time.sleep(1)
            print("Current temperature:", self._query_temperature[2])
            time.sleep(1)

    def shutdown(self):
        self._deactivate_fan()
        self._close_device()
        self._close_driver()

    def _open_driver(self):
        err = sbig.SBIGUnivDrvCommand(sbig.CC_OPEN_DRIVER, None, None)
        check_output(err, "Opened driver", "Failed to open driver")

    def _close_driver(self):
        err = sbig.SBIGUnivDrvCommand(sbig.CC_CLOSE_DRIVER, None, None)
        check_output(err, "Closed driver", "Failed to close driver")

    def _open_device(self):
        params = sbig.OpenDeviceParams()
        params.deviceType = sbig.DEV_USB
        err = sbig.SBIGUnivDrvCommand(sbig.CC_OPEN_DEVICE, params, None)
        check_output(err, "Opened device", "Failed to open device")

    def _close_device(self):
        err = sbig.SBIGUnivDrvCommand(sbig.CC_CLOSE_DEVICE, None, None)
        check_output(err, "Closed device", "Failed to close device")

    def _establish_link(self):
        params = sbig.EstablishLinkParams()
        result = sbig.EstablishLinkResults()
        err = sbig.SBIGUnivDrvCommand(sbig.CC_ESTABLISH_LINK, params, result)
        check_output(err, "Established link with camera", "Unable to establish link with camera")

    def _set_temperature(self, temperature, cool=False):
        strp = sbig.SetTemperatureRegulationParams2()
        strp.regulation = cool
        strp.ccdSetpoint = temperature
        err = sbig.SBIGUnivDrvCommand(sbig.CC_SET_TEMPERATURE_REGULATION2, strp, None)
        if strp.regulation:
            print("Cooling enabled, at a temperature of", temperature)
        else:
            print("Cooling disabled")

    def _query_temperature(self):
        qtsp = sbig.QueryTemperatureStatusParams()
        qtsp.request = sbig.TEMP_STATUS_ADVANCED2
        qtsr = sbig.QueryTemperatureStatusResults2()
        err = sbig.SBIGUnivDrvCommand(sbig.CC_QUERY_TEMPERATURE_STATUS, qtsp, qtsr)
        current_temperature = qtsr.imagingCCDTemperature
        cooling = qtsr.ccdSetpoint
        fan = (qtsr.fanEnabled != sbig.FS_OFF)

        return cooling, fan, current_temperature

    def print_temperature(self):
        cooling, fan, temp = self._query_temperature()
        cooling_str = "Cooling" if cooling else "Not cooling"
        fan_str = "Fan ON" if fan else "FAN OFF"
        temp_str = "Temperature: {0}".format(temp)
        print(temp_str, fan_str, cooling_str, sep="\n")

    def _activate_fan(self):
        mcp = sbig.MiscellaneousControlParams()
        mcp.fanEnable = sbig.FS_ON
        mcp.shutterCommand = sbig.SC_INITIALIZE_SHUTTER
        err = sbig.SBIGUnivDrvCommand(sbig.CC_MISCELLANEOUS_CONTROL, mcp, None)
        check_output(err, "Activated fan", "Failed to activate fan")

    def _deactivate_fan(self):
        mcp = sbig.MiscellaneousControlParams()
        mcp.fanEnable = sbig.FS_OFF
        err = sbig.SBIGUnivDrvCommand(sbig.CC_MISCELLANEOUS_CONTROL, mcp, None)
        check_output(err, "Deactivated fan", "Failed to deactivate fan")

    def spectrum(self, exposure_time, filename):
        dark_image = self.dark(exposure_time)
        light_image = self.light(exposure_time)
        #  using HDU here to allow header to be included in future
        hdu_dark = fits.PrimaryHDU(data=dark_image)
        hdu_light = fits.PrimaryHDU(data=light_image)
        hdu_dark.writeto(filename+"_DarkCurrent.fit", overwrite=True)
        hdu_light.writeto(filename+".fit", overwrite=True)

    def take_image(self, exposure_time, shutter=sbig.SC_OPEN_SHUTTER):
        print("Current temperature:", self._query_temperature[2])
        self._expose(exposure_time, shutter=shutter)
        image = self._readout()
        return image

    def light(self, exposure_time):
        image = self.take_image(exposure_time, shutter=sbig.SC_OPEN_SHUTTER)
        return image

    def dark(self, exposure_time):
        image = self.take_image(exposure_time, shutter=sbig.SC_CLOSE_SHUTTER)
        return image

    def bias(self):
        image = self.take_image(0., shutter=sbig.SC_CLOSE_SHUTTER)
        return image

    def _expose(self, exposure_time, shutter=sbig.SC_OPEN_SHUTTER):
        self._start_exposure(exposure_time, shutter=shutter)
        self._run_exposure(exposure_time)
        self._end_exposure()

    def _start_exposure(self, exposure_time, shutter=sbig.SC_OPEN_SHUTTER):
        sep = sbig.StartExposureParams2()
        mcp = sbig.MiscellaneousControlParams()
        sep.ccd = sbig.CCD_IMAGING
        sep.openShutter = shutter
        sep.abgState = 0
        sep.readoutMode = 0
        sep.top = 0
        sep.left = 0
        sep.height = 510
        sep.width = 767
        sep.exposureTime = long(100 * exposure_time)  # units of 10 millisec
        err = sbig.SBIGUnivDrvCommand(sbig.CC_START_EXPOSURE2, sep, None)
        check_output(err, "Started exposure", "Failed to start exposure")

    def _run_exposure(self, exposure_time):
        time.sleep(exposure_time)
        sep = sbig.StartExposureParams2()
        while status(sbig.CC_START_EXPOSURE2) != sbig.CS_INTEGRATION_COMPLETE:
            pass  # loop until integration finished

    def _end_exposure(self):
        eep = sbig.EndExposureParams()
        eep.ccd = sbig.CCD_IMAGING
        err = sbig.SBIGUnivDrvCommand(sbig.CC_END_EXPOSURE, eep, None)
        check_output(err, "Ended exposure", "Failed to end exposure")
        sep = sbig.StartExposureParams2()
        sep.openShutter = sbig.SC_CLOSE_SHUTTER  # does this actually do anything?

    def _readout(self):
        self._start_readout()
        image = self._readout_data()
        self._end_readout()
        return image

    def _start_readout(self):
        srp = sbig.StartReadoutParams()
        srp.ccd = sbig.CCD_IMAGING
        srp.readoutMode = 0
        srp.top = 0
        srp.left = 0
        srp.height = 510
        srp.width = 767
        err = sbig.SBIGUnivDrvCommand(sbig.CC_START_READOUT, srp, None)
        check_output(err, "Started readout", "Failed to start readout")

    def _readout_data(self):
        rlp = sbig.ReadoutLineParams()
        rlp.ccd = sbig.CCD_IMAGING
        rlp.readoutMode = 0
        rlp.pixelStart = 0
        rlp.pixelLength = 767

        imgbuffer = np.zeros(767, np.uint16)
        img = np.zeros([767, 510], np.uint16)
        for i in range(510):
            err = sbig.SBIGUnivDrvCommand(sbig.CC_READOUT_LINE, rlp, imgbuffer)
            img[:, i] = imgbuffer
            if err != sbig.CE_NO_ERROR:
                print("Readout error at line", i)

        return img

    def _end_readout(self):
        erp = sbig.EndReadoutParams()
        erp.ccd = sbig.CCD_IMAGING
        err = sbig.SBIGUnivDrvCommand(sbig.CC_END_READOUT, erp, None)
        check_output(err, "Ended readout", "Failed to end readout")