from __future__ import print_function
from Sbigudrv import *
import time
import numpy
from matplotlib import pylab
import pyfits
def main(exp_time, filename):
    
    exp_time=exp_time
    closeCam()
    openCam()
    temperature = queryTemperature()
    while temperature > 5.0: 
        time.sleep(1)
        temperature = queryTemperature()
        print(temperature)
    #time.sleep(60)
    #openCam()
    
    gcip=GetCCDInfoParams();
    gcip.request=CCD_INFO_IMAGING
    gcir0=GetCCDInfoResults0(); 
    err = SBIGUnivDrvCommand(CC_GET_CCD_INFO, gcip, gcir0)
    #help(gcir0)
    print('name: ',gcir0.name)
    print('readoutmodes: ',gcir0.readoutModes)
    print('cameratype: ', gcir0.cameraType)
    print('Height: ', gcir0.readoutInfo.height)
    print('Width: ', gcir0.readoutInfo.width)
    print('Mode: ', gcir0.readoutInfo.mode)
    print('Pixelwidth:', gcir0.readoutInfo.pixelWidth)
    print('Gain: ', gcir0.readoutInfo.gain)
    #print gcir0.mode
	
    pylab.ion()
    #pylab.gray()
    for j in numpy.arange(1):
        #print j
        img=takeImg(exp_time)
        darkimg = takeDark(exp_time, SC_CLOSE_SHUTTER)
        #pyfits.writeto("img_10_"+str(j)+".fits",img,clobber=True)
        #img=takeImg(exp_time/10.)
        #pyfits.writeto("img_1_"+str(j)+".fits",img,clobber=True)
        #img=takeImg(exp_time/100.)
        #pyfits.writeto("img_0p1_"+str(j)+".fits",img,clobber=True)
        #img=takeImg(exp_time/1000.)
        #pyfits.writeto("img_0p01_"+str(j)+".fits",img,clobber=True)
        #img=takeImg(exp_time/10000.)
        #pyfits.writeto("img_0p001_"+str(j)+".fits",img,clobber=True)
        #img=takeImg(exp_time*3.)
        #pyfits.writeto("img_30_"+str(j)+".fits",img,clobber=True)
        #pylab.imshow(img,interpolation="nearest")
        #pylab.draw()
        #time.sleep(1)
        #img=takeBias()
        #pyfits.writeto("bias_"+str(j)+".fits",img,clobber=True)
        #time.sleep(1)
        
    #print numpy.std(img)
    #closeCam()
    
	
    print('Saving fits')
    hdu = pyfits.PrimaryHDU(img)
    pyfits.writeto(filename+".fit",img,clobber=True)
    
    hdu_dark = pyfits.PrimaryHDU(darkimg)
    pyfits.writeto(filename+'_DarkCurrent.fit', darkimg, clobber = True)
    print('Done')
    #pylab.imshow(img,interpolation="nearest")
    #pylab.colorbar()
    #pylab.savefig('gelukt.png')
    #pylab.show()
    

	
def takePic(exp_t,shutter):
    startExposure(exp_t,shutter) 
    checkExposure()
    print('exposure gecheckt')
    endExposure()
    startReadout()
    img=readoutLine()
    endReadout()
    temp=queryTemperature()
    return img
	
def takeImg(exp_t):
    return takePic(exp_t,SC_OPEN_SHUTTER)

def takeDummy(exp_t):
    return takePic(exp_t,4)
	
def takeDark(exp_t):
    return takePic(exp_t,SC_CLOSE_SHUTTER)
	
def takeBias():
    return takePic(0,SC_CLOSE_SHUTTER)
	
def takeDark(exp_t, SC_CLOSE_SHUTTER):
	startDarkExposure(exp_t, SC_CLOSE_SHUTTER)
	checkExposure()
	print('DarkExposure gecheckt')
	endExposure()
	startReadout()
	darkimg = readoutLine()
	endReadout()
	temp = queryTemperature()
	Darkhdu = pyfits.PrimaryHDU(darkimg)
	#pylab.clf()
	#pyfits.writeto('DarkCurrent.fits', darkimg, clobber = True)
	#pylab.imshow(darkimg, interpolation = 'nearest')
	#pylab.colorbar()
	#pylab.savefig('dark.png')
	return darkimg

def startDarkExposure(exp_t, shutter):
	print("Take darkcurrent with t_exp: "+str(exp_t)+" s")
	sep = StartExposureParams2()
	mcp=MiscellaneousControlParams()
	sep.ccd = CCD_IMAGING #use imaging CCD
	sep.openShutter = 2 #CLOSE SHUTTER
	sep.abgState = 0 # AntiBloomGate low
	sep.readoutMode=0#RM_1X1#RM_1X1 #no binning
	sep.top=0
	sep.left=0
	sep.height=510
	sep.width=767
	#sep.height=767
	#sep.width=510
	sep.exposureTime = long(100*exp_t) # convert to units of 10 milliseconds
	err=SBIGUnivDrvCommand(CC_START_EXPOSURE2, sep, None)
	if ( err != CE_NO_ERROR ):
		print("exposure start failed with error code: ", err)
	else:
		print("exposure started succesfully")

def startExposure(exp_t,shutter):
    print("start exposure with t_exp: "+str(exp_t)+" s")
    sep = StartExposureParams2()
    mcp=MiscellaneousControlParams()
    #help(sep)
    sep.ccd = CCD_IMAGING #use imaging CCD
    sep.openShutter = 1 #SC_OPEN_SHUTTER
    #sep.openShutter = 0 #SC_LEAVE_SHUTTER
    sep.abgState = 0 # AntiBloomGate low
    sep.readoutMode=0#RM_1X1#RM_1X1 #no binning
    sep.top=0
    sep.left=0
    sep.height=510
    sep.width=767
    #sep.height=767
    #sep.width=510
    sep.exposureTime = long(100*exp_t) # convert to units of 10 milliseconds
    err=SBIGUnivDrvCommand(CC_START_EXPOSURE2, sep, None)
    if ( err != CE_NO_ERROR ):
        print("exposure start failed with error code: ", err)
    else:
        print("exposure started succesfully")
     
def checkExposure():
    cmd=CC_START_EXPOSURE2
    sep=StartExposureParams2()
    #sep.openshutter = 0 #leave shutter alone
    print('status cmd checkExposure:',status(cmd))
    while status(cmd) != CS_INTEGRATION_COMPLETE: #keep looping until camera confirms end of exposure
        pass
	
		
def endExposure():
    eep = EndExposureParams() # end exposing
    eep.ccd = CCD_IMAGING
    err=SBIGUnivDrvCommand(CC_END_EXPOSURE, eep, None)
    sep = StartExposureParams2()
    sep.openShutter = 2 #
    print("Ending exposure")

def status(cmd):
    qcsp = QueryCommandStatusParams()
    qcsr = QueryCommandStatusResults()
    qcsp.command = cmd
  
    err=SBIGUnivDrvCommand(CC_QUERY_COMMAND_STATUS, qcsp, qcsr)
    #print qcsr.status    
    return qcsr.status   
 

def startReadout():
    srp = StartReadoutParams()
    srp.ccd = 0 #CCD_IMAGING
    srp.readoutMode = 0
    srp.top    = 0
    srp.left   = 0
    srp.height = 510
    srp.width  = 767
    #srp.height=767
    #srp.width=510
    err = SBIGUnivDrvCommand(CC_START_READOUT, srp, None)
    if (err != CE_NO_ERROR):
        print("Readout starting failed with error:", err)
    else:
        print("Readout started succesfully")
    

def readoutLine():
    rlp=ReadoutLineParams()
    rlp.ccd= 0 #CCD_IMAGING
    rlp.readoutMode=0#RM_1X1#RM_1X1#RM_1X1
    rlp.pixelStart=0
    rlp.pixelLength=767
    #rlp.pixelLength=510
    imgbuffer=numpy.zeros(767,numpy.uint16)
    img=numpy.zeros([767,510],numpy.uint16)
    for i in numpy.arange(510):
        #print i
        err=SBIGUnivDrvCommand(CC_READOUT_LINE,rlp,imgbuffer)
        img[:,i]=imgbuffer
        if(err != CE_NO_ERROR):
            print("Readout error at line "+str(i))
        
    return img

def endReadout():
	erp = EndReadoutParams()
	erp.ccd = 0 #CCD_IMAGING
	err=SBIGUnivDrvCommand(CC_END_READOUT, erp, None)
	#err=SBIGUnivDrvCommand(CC_UPDATE_CLOCK,None,None)
	#time.sleep(1)
	print("Readout ended")
 

def openCam():
    openDriver()
    openDevice()
    establishLink()
    setTemperature(1,0.0)
    activateFan() #start fan
    mcp=MiscellaneousControlParams()
    mcp.shutterCommand = SC_LEAVE_SHUTTER
    #time.sleep(1)
	
def closeCam():
    deactivateFan() #stop fan
    setTemperature(0,5.)    
    closeDevice()
    closeDriver()
    #time.sleep(1)
	
def openDriver():
    err=SBIGUnivDrvCommand(CC_OPEN_DRIVER,None,None)
    if ( err != CE_NO_ERROR ):
        print("Driver open failed")
    else:
        print("Driver opened")

def openDevice():
    opd=OpenDeviceParams();
    opd.deviceType=DEV_USB
    err=SBIGUnivDrvCommand(CC_OPEN_DEVICE,opd,None)
    if ( err != CE_NO_ERROR ):
        print("Device open failed")
    else:
        print("Device opened")
		
def closeDriver():
    err=SBIGUnivDrvCommand(CC_CLOSE_DRIVER,None,None)
    if ( err != CE_NO_ERROR ):
        print("Driver close failed")
    else:
        print("Driver closed")
    
def closeDevice():
    err=SBIGUnivDrvCommand(CC_CLOSE_DEVICE,None,None)
    if ( err != CE_NO_ERROR ):
        print("Device close failed")
    else:
        print("Device closed")
	
def activateFan():
    mcp=MiscellaneousControlParams()
    mcp.fanEnable=FS_ON
    mcp.shutterCommand = SC_INITIALIZE_SHUTTER
    err=SBIGUnivDrvCommand(CC_MISCELLANEOUS_CONTROL, mcp, None)
    if ( err != CE_NO_ERROR ):
        print("Error on activating fan")
    else:
        print("Fan activated")

    '''
    mcp=MiscellaneousControlParams()
    mcp.fanEnable=FS_ON
    err=SBIGUnivDrvCommand(CC_MISCELLANEOUS_CONTROL, mcp, None)
    if ( err != CE_NO_ERROR ):
    print "Error on activating fan"
    else:
    print "Fan activated"
    '''
	
def deactivateFan():
    mcp=MiscellaneousControlParams()
    mcp.fanEnable=FS_OFF # fan off
    err=SBIGUnivDrvCommand(CC_MISCELLANEOUS_CONTROL, mcp, None)
    if ( err != CE_NO_ERROR ):
        print("Error on deactivating fan")
    else:
        print("Fan deactivated")
    
def setTemperature(cooling,temp):
    
    strp=SetTemperatureRegulationParams2()
    strp.regulation=cooling
    strp.ccdSetpoint=(temp)
    err=SBIGUnivDrvCommand(CC_SET_TEMPERATURE_REGULATION2,strp,None)
    if strp.regulation == 1:
        print("Cooling enabled")
        print("Cooling set to "+str(temp))
    else:
        print("Cooling disabled")
    
def queryTemperature():
    qtsp=QueryTemperatureStatusParams()
    qtsp.request=TEMP_STATUS_ADVANCED2
    qtsr=QueryTemperatureStatusResults2()

    err=SBIGUnivDrvCommand(CC_QUERY_TEMPERATURE_STATUS, qtsp, qtsr)
    print("=========")
    print("Current CCD temperature",qtsr.imagingCCDTemperature)
    print("Current CCD setpoint",qtsr.ccdSetpoint)
    if qtsr.coolingEnabled == 1:
        print("CCD cooling status: on")
    else:
        print("CCD cooling status: off")
    if qtsr.fanEnabled != FS_OFF:
        print("CCD fan status: on")
    else:
        print("CCD fan status: off")
    print("=========")
    return qtsr.imagingCCDTemperature

#def c2ad(temp):
#    r=3.*numpy.exp(numpy.log(2.57)*(25.-numpy.float32(temp))/25.)
#    ad=numpy.int32(4096./((10./r)+1.))
#    if ad < 1:
#        ad=1
#    if ad> 4095:
#        ad=4095
#    return numpy.int32(ad)
#def ad2c(ad):
#    if ad < 1:
#        ad=1
#    if ad > 4095:
#        ad=4095
#    r=10./(4096./numpy.float32(ad)-1.)
#    return (25.-25.*(numpy.log(r/3.)/numpy.log(2.57)))
    


def establishLink():
    elp = EstablishLinkParams()
    elr = EstablishLinkResults();
    err = SBIGUnivDrvCommand(CC_ESTABLISH_LINK, elp, elr);
    
    print('elr.cameratype: ', elr.cameraType)
    if ( err != CE_NO_ERROR ):
        print("establishLink failed")
        print("errorcode: ",err)
    else:
        print("Link established")


