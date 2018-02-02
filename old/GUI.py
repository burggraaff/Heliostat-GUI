#!/usr/bin/python

#			Tutorial from:
#https://pythonprogramming.net/plotting-live-bitcoin-price-data-tkinter-matplotlib/

from __future__ import print_function

import sys

if sys.version_info[0] < 3:
	import Tkinter as tk
	from Tkinter import *
	import ttk
	
else:
	import tkinter as tk
	from tkinter import *
	#from tkinter import ttk

import urllib
import numpy as np
import pyfits
import math
import ephem
import datetime

import matplotlib.image as mpimg
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as p
import matplotlib.animation as animation

from astropy import coordinates as coord
from astropy import units as u

from PIL import Image
from PIL import ImageOps, ImageFont, ImageDraw

import Fitting_script as fs

#hiermee besturen we de camera
sys.path.insert(0, '../sbig')
import proggel as proggel


LARGE_FONT= ("Minion Pro", 14)
LABEL_FONT = ('Minion Pro', 16)

class Page(tk.Frame):
	def __init__(self, *args, **kwargs):
		tk.Frame.__init__(self, *args, **kwargs)
	def show(self):
		self.lift()

class HelioGUI(tk.Frame):			#parentheses are not needed, tk.Tk means we inherit everything from the tk.Tk class

	#this is a method, init will always run when class is called upon
	#args are parameters, kwargs dictionaries
	def __init__(self, parent, *args, **kwargs):		
		
		tk.Frame.__init__(self, parent, *args, **kwargs)	#initialize the inherited class
		
		#tk.Tk.iconbitmap(self, default = 'clienticon.icon') #way to set the client icon
		#tk.Frame.wm_title(self, 'Helio GUI')
		
		self.myParent = parent
		
		self.container = tk.Frame(self)				#just defining a container
		self.container.grid(row = 0, column = 0, sticky = tk.NSEW)
		
		self.myParent.grid_rowconfigure(0, weight = 1)
		self.myParent.grid_columnconfigure(0, weight = 1)	
		
		
		self.frames = {} #empty dictionary		
		#frame = BTCe_Page(container, self)
		#self.frames[BTCe_Page] = frame
		#frame.grid(row = 0, column = 0, sticky = 'nsew')

		for F in (StartPage, Visitor_Page, Spectrum_Page):
			frame = F(self.container, self)
			self.frames[F] = frame
			frame.grid(row = 0, column = 0, sticky = tk.NSEW)
			self.container.grid_rowconfigure(1, weight = 1)
			self.container.grid_columnconfigure(1, weight = 1)
			
			col_count, row_count = frame.grid_size()
			#print(col_count, row_count)
			for row in xrange(row_count):
				frame.grid_rowconfigure(row, weight = 1)
		
			for col in xrange(col_count):
				frame.grid_columnconfigure(col, weight = 1)
			
			
		self.show_frame(StartPage)	
		
	def show_frame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()				#brings the frame to the top for the user to see
		
class StartPage(Page):
	
	def __init__(self, parent, controller):
	
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="""GUI voor de bediening van de spectrograaf en het plotten van het spectrum van de Zon!""", font = LABEL_FONT)
		label.grid(row = 0, column = 2, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		
		button = tk.Button(self, text = 'Bezoekersscherm', 
							command = lambda: controller.show_frame(Visitor_Page), font = LARGE_FONT)
		button.grid(row = 1, column = 2, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		
		button1 = tk.Button(self, text = 'Studentenscherm', 
							command = lambda: controller.show_frame(Spectrum_Page), font = LARGE_FONT)
		button1.grid(row = 2, column = 2, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
						
		button3 = tk.Button(self, text = 'Update de Zon!', command = self.RetrieveSun, font = LARGE_FONT)
		button3.grid(row = 3, column = 2, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)

		button2 = tk.Button(self, text = 'Afsluiten',
							command = self.Quit, font = LARGE_FONT)

		button2.grid(row = 4, column = 2, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)

		fig = p.figure(figsize = (7,7))
		canvas = FigureCanvasTkAgg(fig, self)
		canvas.get_tk_widget().grid(row = 5, column = 2, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		
		col_count, row_count = self.grid_size()
		print(col_count, row_count)
		for row in xrange(row_count):
			self.grid_rowconfigure(row, weight = 1)
		
		for col in xrange(col_count):
			self.grid_columnconfigure(col, weight = 1)
		
	def Quit(self):
		root.quit()
		root.destroy()
		
	def RetrieveSun(self):
		print("Updating the image of the Sun!")
		url = 'http://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg'
		urllib.urlretrieve(url, 'dezon.jpg')
		img = mpimg.imread('dezon.jpg')
		p.figure(1)
		p.clf()
		p.imshow(img)
		p.gcf().canvas.draw()
		#Updates the sun after a number of milliseconds
		#The SDO website updates their images every 15 minutes (900 seconds)
		self.after(900*1000, self.RetrieveSun) 
		
class Visitor_Page(Page):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		
		self.begin = tk.Button(self, text = 'Terug naar Beginscherm',
					command = lambda: controller.show_frame(StartPage))
		self.begin.grid(row = 0, column = 0, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)

		self.student = tk.Button(self, text = 'Naar Studentenscherm',
					command = lambda: controller.show_frame(Spectrum_Page))
		self.student.grid(row = 0, column = 2, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2)
		
		self.afsluiten = tk.Button(self, text="Afsluiten",
					command = self.Quit)
		self.afsluiten.grid(row = 0, column = 4, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2)
		
		
		self.NeemOpname = tk.Button(self, text = 'Opname!', command = lambda: proggel.main(eval('0.04'), 'Bezoekers1'))
		self.NeemOpname.grid(row = 1, column = 2, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2)
		
		self.plot = tk.Button(self, text="Plot!", command = self.firstmeasurement)
		self.plot.grid(row = 1, column = 4, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2)

		self.zon = tk.Button(self, text = 'Update de Zon!', command = self.RetrieveSun)
		self.zon.grid(row = 1, column = 0, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2) 
		
		
		fig = p.figure(figsize = (4,4))
		canvas = FigureCanvasTkAgg(fig, self)
		canvas.get_tk_widget().grid(row = 2, column = 0, padx = 5, sticky = 'nesw', columnspan = 2)
		
		fig1 = p.figure(figsize = (6,4))
		canvas1 = FigureCanvasTkAgg(fig1, self)
		canvas1.get_tk_widget().grid(row = 2, column = 2, padx = 5, pady= 2.5, sticky = 'nesw', columnspan = 2)

		fig2 = p.figure(figsize = (6,4))
		canvas2 = FigureCanvasTkAgg(fig2, self)
		canvas2.get_tk_widget().grid(row = 2, column = 4, padx = 5, pady = 2.5, sticky = 'nesw', columnspan = 2)
		

		self.NeemOpname1 = tk.Button(self, text = 'Opname!', command = lambda: proggel.main(eval('0.04'), 'Bezoekers2'))
		self.NeemOpname1.grid(row = 3, column = 2, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2)
		
		self.plot1 = tk.Button(self, text="Plot!", command = self.secondmeasurement)
		self.plot1.grid(row = 3, column = 4, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2)
		
		
		#Gedraaide zon
		
		self.gedraaidezon = tk.Label(self, text = 'De geroteerde Zon zoals te zien op het scherm, de blauwe lijn is de evenaar.')
		self.gedraaidezon.grid(row = 3, column = 0, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		
		fig = p.figure(figsize = (4,4))
		canvas = FigureCanvasTkAgg(fig, self)
		canvas.get_tk_widget().grid(row = 4, column = 0, padx = 5, sticky = 'news')

		fig3 = p.figure(figsize = (6,4))
		canvas3 = FigureCanvasTkAgg(fig3, self)
		canvas3.get_tk_widget().grid(row = 4, column = 2, padx = 5, pady = 2.5, sticky = 'nesw', columnspan = 2)
		
		fig4 = p.figure(figsize = (6,4))
		canvas4 = FigureCanvasTkAgg(fig4, self)
		canvas4.get_tk_widget().grid(row = 4, column = 4, padx = 5, pady = 2.5, sticky = 'nesw', columnspan = 2)
		

		#Text boxes
		'''
		s = 'CHECK DEZE TEKST!'
		self.area1 = tk.Text(self,width = 50, height = 10)
		self.area1.insert(tk.END,s)
		self.area1.grid(row = 5, column = 2, sticky = 'w', pady=5, padx = 5, columnspan = 2)

		s1 = 'EN CHECK DEZE TEKST OOK!'
		self.area2 = tk.Text(self, width = 50, height = 10)
		self.area2.insert(tk.END,s1)
		self.area2.grid(row = 5, column = 4, sticky = 'w', pady=5, padx = 5, columnspan = 2)
		'''
		
	def Quit(self):
		root.quit()
		root.destroy()
	'''
	def RetrieveSun(self):
		print("Updating the image of the Sun!")
		url = 'http://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg'
		urllib.urlretrieve(url, 'dezon.jpg')
		img = mpimg.imread('dezon.jpg')
		p.figure(2)
		p.clf()
		p.imshow(img)
		p.gcf().canvas.draw()
		#Updates the sun after a number of milliseconds
		#The SDO website updates their images every 15 minutes (900 seconds)
		self.after(900*1000, self.RetrieveSun) 
	'''
	def RetrieveSun(self):
		url = 'http://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg'
		#urllib.request.urlretrieve(url, 'dezon.jpg')
		urllib.urlretrieve(url, 'dezon.jpg')
		#img1 = mpimg.imread('dezon.jpg')
		img = Image.open('dezon.jpg')
		
		#Merging the solar image with NESW-image
		bottom = Image.open('dezon.jpg')
		top = Image.open('Overlay.jpg')
		
		r,g,b = top.split()
		top = Image.merge("RGB",(r,g,b))
		mask = Image.merge("L", (b,))
		bottom.paste(top, (0,0), mask)
		bottom.save('samen.jpg')
				
		projected_img = ImageOps.flip(bottom) #Het beeld is Noord-Zuid gespiegeld
		projected_img = ImageOps.mirror(projected_img)
		
		
		RotationAngle = 24  #Beeld 24 graden geroteerd tenopzichte van loodrecht (naar links kijkend vanaf projectie scherm, dus naar rechts kijkend NAAR scherm)!!
		
		
		#Daar komt ook bij dat de Aarde ten opzichte van de zon 23.43707 graden gedraaid is
		#dit varieert van -23.43707 graden naar +23.43707 graden gedurende het jaar
		#sin met 0 op summer solstice (21 juni) en op winter solstice (21 december)
		#Wanneer is het 0?
		
		x = np.arange(0,365.25,0.25)
		y = [23.43707*math.sin(2*math.pi*(i*360.0/365.0 - 172*360.0/365.0)) for i in x] #in degrees
		day_of_year = datetime.datetime.now().timetuple().tm_yday
		extra_angle = y[day_of_year]
		#dec = 23.45*math.pi/180 * math.sin(2*math.pi*((284+day_of_year)/36.25)) 
		
		################
		#aantal uur tot/vanaf plaatselijke noon
		now = datetime.datetime.now()
		today = now.date()
		noon = datetime.time(hour = 12)
		noon_today = datetime.datetime.combine(today, noon)
		
		diff = now - noon_today
		minutes, seconds = divmod(diff.total_seconds(), 60)
		hours = minutes/60.0 + seconds/360.0
		degrees = hours*15.0
		##############
		
		RotationAngle = RotationAngle - degrees - extra_angle
		print('Hour angle degrees:', degrees)
		print('Angle based on day of the year:', extra_angle)
		print('Rotation angle:', RotationAngle)
		
		
		img2 = projected_img.rotate(-RotationAngle)
		

		
		
		
		###################		

		p.figure(2)
		p.clf()
		p.imshow(bottom)
		p.plot([0,1024],[512,512])
		p.xlim(0,1024)
		p.ylim(0,1024)
		p.gca().invert_yaxis()
		p.gcf().canvas.draw()
		
		#----------------
		
		p.figure(5)
		p.clf()
		
		centerX, centerY = 512, 512
				
		xdisp = 512.0*math.cos(math.radians(RotationAngle))
		ydisp = 512.0*math.sin(math.radians(RotationAngle))
		
		p.xlim(0,1024)
		p.ylim(0,1024)
		p.gca().invert_yaxis()
		#p.gca().invert_xaxis()
		p.plot([centerX-xdisp, centerX+xdisp], [centerY-ydisp,centerY+ydisp])
		###########

		p.imshow(img2)
		
		p.gcf().canvas.draw()
		
		#Updates the sun after a number of milliseconds
		#The SDO website updates their images every 15 minutes (900 seconds)
		self.after(900*1000, self.RetrieveSun) 	
		
	def firstmeasurement(self):	
		p.figure(3)
		p.clf()
		data = pyfits.getdata("Bezoekers1.fit")
		p.imshow(data.T, interpolation = 'nearest', origin = 'upper')
		#tp.DisplaySpectrum()
		#tp.AnderePlot()
		p.gcf().canvas.draw()

		p.figure(4)
		p.clf()
		fs.readdata("Bezoekers1.fit")
		p.gcf().canvas.draw()
		
	def secondmeasurement(self):
		p.figure(6)
		p.clf()
		data = pyfits.getdata("Bezoekers2.fit")
		p.imshow(data.T, interpolation = 'nearest', origin = 'upper')
		#tp.DisplaySpectrum()
		#tp.AnderePlot()
		p.gcf().canvas.draw()

		p.figure(7)
		p.clf()
		fs.readdata("Bezoekers2.fit")
		p.gcf().canvas.draw()


class Spectrum_Page(Page):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)


		self.button2 = tk.Button(self, text = 'Terug naar Beginscherm',
					command = lambda: controller.show_frame(StartPage))
		self.button2.grid(row = 0, column = 0, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2)

		self.button4 = tk.Button(self, text = 'Naar Bezoekersscherm',
					command = lambda: controller.show_frame(Visitor_Page))
		self.button4.grid(row = 0, column = 2, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2)
		
		self.draw_button3 = tk.Button(self, text="Afsluiten",
					command = self.Quit)
		self.draw_button3.grid(row = 0, column = 4, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2)
		
				
		self.draw_button1 = tk.Button(self, text = 'Update de Zon!', command = self.RetrieveSun)
		self.draw_button1.grid(row = 3, column = 0, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		
		self.invoerlabel = tk.Label(self, text = 'Geef hier de gewenste integratietijd!')
		self.invoerlabel.grid(row = 2, column = 4, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		self.Invoer = tk.Entry(self)
		self.Invoer.grid(row = 3, column = 4)
		
		self.invoernaam = tk.Label(self, text = 'Geef hier de gewenste bestandsnaam.')
		self.invoernaam.grid(row = 2, column = 5, padx = 5, pady = 2.5, sticky = 'nesw', columnspan = 1)
		self.naam = tk.Entry(self)
		self.naam.grid(row = 3, column = 5)
		
		
		self.NeemOpname = tk.Button(self, text = 'Opname!', command = lambda: proggel.main(eval(self.Invoer.get()), self.naam.get()))
		self.NeemOpname.grid(row = 3, column = 2, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
			
		self.draw_button = tk.Button(self, text="Plot!", command = self.firstmeasurement)
		self.draw_button.grid(row = 3, column = 3, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		
		#referentie zon
		fig = p.figure(figsize = (4,4))
		canvas = FigureCanvasTkAgg(fig, self)
		canvas.get_tk_widget().grid(row = 4, column = 0, padx = 5, sticky = 'news')
		
		#Meting 1
		fig1 = p.figure(figsize = (6,4))
		canvas1 = FigureCanvasTkAgg(fig1, self)
		canvas1.get_tk_widget().grid(row = 4, column = 2, padx = 5, sticky = 'news', columnspan = 2)
		toolbar1 = NavigationToolbar2TkAgg(canvas1, self)
		toolbar1.update()
		toolbar1.grid(row = 5, column = 2, sticky = 'news', columnspan = 2)
		
		
		#Meting 1
		fig2 = p.figure(figsize = (6,4))
		canvas2 = FigureCanvasTkAgg(fig2, self)
		canvas2.get_tk_widget().grid(row = 4, column = 4, padx = 5, sticky = 'news', columnspan = 2)
		toolbar = NavigationToolbar2TkAgg(canvas2, self)
		toolbar.update()
		toolbar.grid(row = 5, column = 4, sticky = 'news', columnspan = 2)
		
		self.invoerlabel1 = tk.Label(self, text = 'Geef hier de gewenste integratietijd!')
		self.invoerlabel1.grid(row = 6, column = 4, padx = 5, pady = 2.5, sticky ='nesw')
		self.Invoer1 = tk.Entry(self)
		self.Invoer1.grid(row = 7, column = 4)
		
		self.invoernaam1 = tk.Label(self, text = 'Geef hier de gewenste bestandsnaam.')
		self.invoernaam1.grid(row = 6, column = 5, padx = 5, pady = 2.5, sticky = 'nesw')
		self.naam1 = tk.Entry(self)
		self.naam1.grid(row = 7, column = 5)
		
		self.NeemOpname1 = tk.Button(self, text = 'Opname!', command = lambda: proggel.main(eval(self.Invoer1.get()), self.naam1.get()))
		self.NeemOpname1.grid(row = 7, column = 2, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		
		self.draw_button = tk.Button(self, text="Plot!", command = self.secondmeasurement)
		self.draw_button.grid(row = 7, column = 3, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		
		#Gedraaide zon
		
		self.gedraaidezon = tk.Label(self, text = 'De geroteerde Zon zoals te zien op het scherm, de blauwe lijn is de evenaar.')
		self.gedraaidezon.grid(row = 7, column = 0, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		
		fig = p.figure(figsize = (4,4))
		canvas = FigureCanvasTkAgg(fig, self)
		canvas.get_tk_widget().grid(row = 8, column = 0, padx = 5, sticky = 'news')

		#Meting 2
		fig3 = p.figure(figsize = (6,4))
		canvas3 = FigureCanvasTkAgg(fig3, self)
		canvas3.get_tk_widget().grid(row = 8, column = 2, padx = 5, pady = 2.5, sticky = 'nesw', columnspan = 2)
		toolbar3 = NavigationToolbar2TkAgg(canvas3, self)
		toolbar3.update()
		toolbar3.grid(row = 9, column = 2, sticky = 'news', columnspan = 2)
		
		
		#Meting 2
		fig4 = p.figure(figsize = (6,4))
		canvas4 = FigureCanvasTkAgg(fig4, self)
		canvas4.get_tk_widget().grid(row = 8, column = 4, padx = 5, pady = 2.5, sticky = 'nesw', columnspan = 2)
		toolbar4 = NavigationToolbar2TkAgg(canvas2, self)
		toolbar4.update()
		toolbar4.grid(row = 9, column = 4, sticky = 'news', columnspan = 2)
		
		

		#Text boxes
		'''
		s = 'CHECK DEZE TEKST!'
		self.area1 = tk.Text(self,width = 50, height = 10)
		self.area1.insert(tk.END,s)
		self.area1.grid(row = 5, column = 2, sticky = 'w', pady=5, padx = 5, columnspan = 2)

		s1 = 'EN CHECK DEZE TEKST OOK!'
		self.area2 = tk.Text(self, width = 50, height = 10)
		self.area2.insert(tk.END,s1)
		self.area2.grid(row = 5, column = 4, sticky = 'w', pady=5, padx = 5, columnspan = 2)
		'''
	def Quit(self):
		root.quit()
		root.destroy()

	def RetrieveSun(self):
		url = 'http://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg'
		#urllib.request.urlretrieve(url, 'dezon.jpg')
		urllib.urlretrieve(url, 'dezon.jpg')
		#img1 = mpimg.imread('dezon.jpg')
		img = Image.open('dezon.jpg')
		
		
		#Merging the solar image with NESW-image
		bottom = Image.open('dezon.jpg')
		top = Image.open('Overlay.jpg')
		
		r,g,b = top.split()
		top = Image.merge("RGB",(r,g,b))
		mask = Image.merge("L", (b,))
		bottom.paste(top, (0,0), mask)
		bottom.save('samen.jpg')
				
		projected_img = ImageOps.flip(bottom) #Het beeld is Noord-Zuid gespiegeld
		projected_img = ImageOps.mirror(projected_img)
		

		
		RotationAngle = 24  #Beeld 24 graden geroteerd tenopzichte van loodrecht (naar links kijkend vanaf projectie scherm, dus naar rechts kijkend NAAR scherm)!!
		
		#Daar komt ook bij dat de Aarde ten opzichte van de zon 23.43707 graden gedraaid is
		#dit varieert van -23.43707 graden naar +23.43707 graden gedurende het jaar
		#sin met 0 op summer solstice (21 juni) en op winter solstice (21 december)
		#Wanneer is het 0?
		
		x = np.arange(0,365.25,0.25)
		y = [23.43707*math.sin(2*math.pi*(i*360.0/365.0 - 172*360.0/365.0)) for i in x] #in degrees
		day_of_year = datetime.datetime.now().timetuple().tm_yday
		extra_angle = y[day_of_year]
		#dec = 23.45*math.pi/180 * math.sin(2*math.pi*((284+day_of_year)/36.25)) 
		
		################
		#aantal uur tot/vanaf plaatselijke noon
		now = datetime.datetime.now()
		today = now.date()
		noon = datetime.time(hour = 12)
		noon_today = datetime.datetime.combine(today, noon)
		
		diff = now - noon_today
		minutes, seconds = divmod(diff.total_seconds(), 60)
		hours = minutes/60.0 + seconds/360.0
		degrees = hours*15.0
		##############
		
		RotationAngle = RotationAngle - degrees - extra_angle
		print('Hour angle degrees:', degrees)
		print('Angle based on day of the year:', extra_angle)
		print('Rotation angle:', RotationAngle)
		
		img2 = projected_img.rotate(-RotationAngle)
				
		
		###################		

		p.figure(8)
		p.clf()
		p.imshow(bottom)
		p.plot([0,1024],[512,512])
		p.xlim(0,1024)
		p.ylim(0,1024)
		p.gca().invert_yaxis()
		p.gcf().canvas.draw()
		
		#----------------
		
		p.figure(11)
		p.clf()
		
		###### - Line showing the equator
		centerX, centerY = 512, 512
				
		xdisp = 512.0*math.cos(math.radians(RotationAngle))
		ydisp = 512.0*math.sin(math.radians(RotationAngle))
		
		p.xlim(0,1024)
		p.ylim(0,1024)
		p.gca().invert_yaxis()
		#p.gca().invert_xaxis()
		p.plot([centerX-xdisp, centerX+xdisp], [centerY-ydisp,centerY+ydisp])
		###########

		#p.imshow(img2)
		p.imshow(img2)
		
		p.gcf().canvas.draw()
		
		#Updates the sun after a number of milliseconds
		#The SDO website updates their images every 15 minutes (900 seconds)
		self.after(900*1000, self.RetrieveSun) 


	def firstmeasurement(self):	
		p.figure(9)
		p.clf()
		#data = pyfits.getdata(self.naam.get()+".fit")
				
		raw_data = pyfits.getdata(self.naam.get()+".fit")
		dark_data = pyfits.getdata(self.naam.get()+"_DarkCurrent.fit")
		
		dark_data  = dark_data.astype(np.int16) #Deze twee .astype() handelingen zijn nodig om te data in het correcte format te zetten
		raw_data  = raw_data.astype(np.int16)   #Negatieve waarden worden anders onjuist behandeld
		data = raw_data - dark_data
		data = data.T
		
		p.imshow(data)#, interpolation = 'nearest', origin = 'upper')
		#tp.DisplaySpectrum()
		#tp.AnderePlot()
		p.gcf().canvas.draw()

		p.figure(10)
		p.clf()
		fs.readdata(data)
		#fs.readdata(self.naam.get()+".fit")
		p.gcf().canvas.draw()
		
	def secondmeasurement(self):
		p.figure(12)
		p.clf()
		raw_data = pyfits.getdata(self.naam1.get()+".fit")
		dark_data = pyfits.getdata(self.naam1.get()+"_DarkCurrent.fit")
		
		dark_data  = dark_data.astype(np.int16) #Deze twee .astype() handelingen zijn nodig om te data in het correcte format te zetten
		raw_data  = raw_data.astype(np.int16)   #Negatieve waarden worden anders onjuist behandeld
		data = raw_data - dark_data
		data = data.T
			
		p.imshow(data)#, interpolation = 'nearest', origin = 'upper')
		#tp.DisplaySpectrum()
		#tp.AnderePlot()
		p.gcf().canvas.draw()

		p.figure(13)
		p.clf()
		fs.readdata(data)
		#fs.readdata(self.naam1.get()+".fit")
		p.gcf().canvas.draw()
		
		
if __name__ == "__main__":
	root = tk.Tk()	
	app = HelioGUI(root)
	app.pack(side = 'top', fill = 'both', expand = True)
	#root.wm_geometry('1400x900')
	root.attributes("-fullscreen", True)

	root.mainloop()
	
	