from __future__ import print_function, division
import time
import numpy

import Sbigudrv as sbig

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

    def shutdown(self):
        self._deactivate_fan()
        self._close_device()
        self._close_driver()

    def _open_driver(self):
        err = sbig.SBIGUnivDrvCommand(sbig.CC_OPEN_DRIVER, None, None)
        self.check_output(err, "Opened driver", "Failed to open driver")

    def _close_driver(self):
        err = sbig.SBIGUnivDrvCommand(sbig.CC_CLOSE_DRIVER, None, None)
        self.check_output(err, "Closed driver", "Failed to close driver")

    def _open_device(self):
        params = sbig.OpenDeviceParams()
        params.deviceType = sbig.DEV_USB
        err = sbig.SBIGUnivDrvCommand(sbig.CC_OPEN_DEVICE, params, None)
        self.check_output(err, "Opened device", "Failed to open device")

    def _close_device(self):
        err = sbig.SBIGUnivDrvCommand(sbig.CC_CLOSE_DEVICE, None, None)
        self.check_output(err, "Closed device", "Failed to close device")

    def _establish_link(self):
        params = sbig.EstablishLinkParams()
        result = sbig.EstablishLinkResults()
        err = sbig.SBIGUnivDrvCommand(sbig.CC_ESTABLISH_LINK, params, result)
        self.check_output(err, "Established link with camera", "Unable to establish link with camera")

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
        current_temperature = qtsd.imagingCCDTemperature
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
        self.check_output(err, "Activated fan", "Failed to activate fan")

    def _deactivate_fan(self):
        mcp = sbig.MiscellaneousControlParams()
        mcp.fanEnable = sbig.FS_OFF
        err = sbig.SBIGUnivDrvCommand(sbig.CC_MISCELLANEOUS_CONTROL, mcp, None)
        self.check_output(err, "Deactivated fan", "Failed to deactivate fan")

    @staticmethod
    def check_output(output, msg_good="", msg_bad="Failure!"):
        if output == sbig.CE_NO_ERROR:
            print(msg_good)
        else:
            raise ValueError(msg_bad + "\nError code: {0}".format(output))