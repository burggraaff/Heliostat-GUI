#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import pyfits
from scipy.optimize import curve_fit
from scipy.signal import find_peaks_cwt as p
#import matplotlib.ticker as ticker
from astropy.modeling import models
from astropy.modeling import fitting

import sys
import os
import math

def BackgroundFitting(data):
	backgroundrows = np.append(np.arange(0, 300), np.arange(375, 510))
	rows = np.arange(data.shape[0])
	bkg = np.zeros_like(data)
	for col in np.arange(data.shape[1]):
		pfit = np.polyfit(backgroundrows, data[backgroundrows, col], 2)
		bkg[:,col] = np.polyval(pfit, rows)
	
	bkg = bkg.astype(np.int16)
	
	data_bkg = data - bkg
	return data_bkg

	
def readdata(data):
	#data = pyfits.getdata('1sec299driekwart2.FIT')
	#data = data.T
	bkg = BackgroundFitting(data)
	y = np.sum(bkg, axis = 0)
	x = np.arange(767)
	
	points = []
	i = 0
	while i<=len(x):
		points.append(np.max(y[i:i+25]))
		i+=25
		
	from scipy.interpolate import UnivariateSpline
	old_indices = np.arange(0, len(points))
	new_length = 767
	new_indices = np.linspace(0, len(points)-1, new_length)
	spl = UnivariateSpline(old_indices, points, k = 3, s =1)
	new_array = spl(new_indices)
	y1 = y/new_array

	#z = np.polyfit(x,y,3)
	#p = np.poly1d(z)
	#y1 = y / p(x)
	plt.plot(x,y1)

'''
data = pyfits.getdata('1sec299driekwart2.FIT')
for file in os.listdir('./'):
	if file.endswith('.fit') or file.endswith('.FIT'):
		print(file)
		data = pyfits.getdata(file)
		#data_darkcurrent = pyfits.getdata(darkcurrent)
		#data = data - data_darkcurrent
		data_bkg = BackgroundFitting(data)
		
		y = np.sum(data_bkg, axis = 0)
		x = np.arange(767)
		z = np.polyfit(x,y,3)
		p = np.poly1d(z)
		y1 = y / p(x)
		plt.plot(x,y1)
		#plt.plot(x,y, '.', x, p(x), '-')
		plt.xlim(0,760)
		plt.savefig(file[:-4]+'.png')
		plt.clf()
'''
'''
#Gehele spectrum
a,b =np.loadtxt('../GeheleSpectrumBass2000.txt', dtype = float, unpack = True)		
idx = (a > 6289.13)* (a < 6314.348 ) #Voor 5sec298kwart4.FIT
c = b[np.where(idx)]
aa = a[np.where(idx)]
aa = aa/10.0
c1 = c / np.max(c)
cc = np.linspace(0,767, len(c1))

#fitting wavelengths
centralp, centralw, slope = 392.246, 630.1988, 0.00332409972
p = np.arange(len(y1))
w = centralw + slope*(p-centralp)
'''


def gauss_function(x, a, x0, sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))

def ReadinandPlot():
	data = pyfits.getdata("firstlight.fits")#lab
	data = data.astype(np.int16)
	darkdata = pyfits.getdata('DarkCurrent.fits')
	darkdata = darkdata.astype(np.int16)
	#print(np.shape(data))
	data = np.subtract(data,darkdata)
	
	y = np.sum(data.T, axis=0)/767.0

	y = [i - np.mean(y[0:570]) for i in y]
	y = np.asarray(y)
	x = np.arange(767)

	x2 = np.linspace(0,767,1000)


	#do the fit!
	popt, pcov = curve_fit(gauss_function, x, y)

	x1 = x[(x>450)&(x<500)]
	y1 = y[(x>450)&(x<500)]
	y1 = [i - np.mean(y[0:450]) for i in y1]
	mean = np.mean(x1)
	std = np.std(x1)
	Gaus(x, y, x1,y1,mean,std)

	#plt.show()
	#print(np.min(y))
	
def Gaus(x, y, xfit, yfit, mean, std):
	#print(len(xfit), len(yfit))
	g_init = models.Gaussian1D(amplitude=max(yfit), mean=mean, stddev=std)
	fit_g = fitting.LevMarLSQFitter()
	g = fit_g(g_init, xfit, yfit)
	stddev = g.stddev
	#print(g)
	plt.plot(xfit, g(xfit), 'r-', lw=2)
	#y = [i - np.mean(y[0:435]) for i in y]
	plt.plot(x, y)
	plt.ylim(0,max(y)+10)

	#plt.xlim(400,450)
	FWHM = 2*np.sqrt(2.0*np.log(2.0))*stddev 
	#FWHMv = FWHM*(c/mean)
	
	print('FWHM: ', FWHM)

	Y = g(xfit)
	half_max = max(Y)/2
	plt.text(100, max(y)-5, 'FWHM: %s pixels' %FWHM)
	
	return FWHM
#print popt, pcov

#FWHM = 2*np.sqrt(2*np.log(2))*1.55

#plt.figure()
#plt.plot(data)
#plt.plot(x,y, color = "blue")

#plt.savefig('mooi.png')
