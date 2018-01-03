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
	
import tkMessageBox

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

import tkFont

LARGE_FONT= ('TkDefaultFont', 14)
LABEL_FONT=('TkDefaultFont', 16)

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


		for F in (Student_Ned,Student_Eng):
			frame = F(self.container, self)
			self.frames[F] = frame
			frame.grid(row = 0, column = 0, sticky = tk.NSEW)
			self.container.grid_rowconfigure(1, weight = 1)
			self.container.grid_columnconfigure(1, weight = 1)
			
		self.show_frame(Student_Ned)	
		
	def show_frame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()				#brings the frame to the top for the user to see

class Student_Ned(Page):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		
		#Row 0
		self.langbutton = tk.Button(self, text = 'ENG',command = lambda: controller.show_frame(Student_Eng))
		self.langbutton.grid(row = 0, column = 0, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2)
		self.quitbutton = tk.Button(self, text="Afsluiten",command = lambda: Quit(self), bg='red')
		self.quitbutton.grid(row = 0, column = 4, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2)
		#Row 2 & 3
		self.invoerlabel = tk.Label(self, text = 'Geef hier de gewenste integratietijd!')
		self.invoerlabel.grid(row = 2, column = 4, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		self.Invoer = tk.Entry(self)
		self.Invoer.grid(row = 3, column = 4)
		
		self.invoernaam = tk.Label(self, text = 'Geef hier de gewenste bestandsnaam.')
		self.invoernaam.grid(row = 2, column = 5, padx = 5, pady = 2.5, sticky = 'nesw', columnspan = 1)
		self.naam = tk.Entry(self)
		self.naam.grid(row = 3, column = 5)
		# Row 3	
		self.updatesun = tk.Button(self, text = 'Update de Zon!', command= lambda: RetrieveSun(self,1))
		self.updatesun.grid(row = 3, column = 0, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		self.recordbutton = tk.Button(self, text = 'Opname!', command = lambda: proggel.main(eval(self.Invoer.get()), self.naam.get()))
		self.recordbutton.grid(row = 3, column = 2, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		self.plotbutton = tk.Button(self, text="Plot!", command = lambda: plotmeasurement(self,5))
		self.plotbutton.grid(row = 3, column = 3, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		
		#referentie zon
		fig1 = p.figure(figsize = (3,2.5))
		canvas1 = FigureCanvasTkAgg(fig1, self)
		canvas1.get_tk_widget().grid(row = 4, column = 0, padx = 5, sticky = 'news')
		fig1.canvas.mpl_connect('button_press_event',lambda event: printcoords(event))	
		
		#Meting 1
		fig2 = p.figure(figsize = (3,2.5))
		canvas2 = FigureCanvasTkAgg(fig2, self)
		canvas2.get_tk_widget().grid(row = 4, column = 2, padx = 5, sticky = 'news', columnspan = 2)
		toolbar1 = NavigationToolbar2TkAgg(canvas2, self)
		toolbar1.update()
		toolbar1.grid(row = 5, column = 2, sticky = 'news', columnspan = 2)
	
		#Meting 1
		fig3 = p.figure(figsize = (3,2.5))
		canvas3 = FigureCanvasTkAgg(fig3, self)
		canvas3.get_tk_widget().grid(row = 4, column = 4, padx = 5, sticky = 'news', columnspan = 2)
		toolbar2 = NavigationToolbar2TkAgg(canvas3, self)
		toolbar2.update()
		toolbar2.grid(row = 5, column = 4, sticky = 'news', columnspan = 2)
		
		#Row 7, 8 Info
		#Gedraaide zon
		self.suninfo = tk.Label(self, text = 'De geroteerde Zon zoals te zien op het scherm, de blauwe lijn is de evenaar.')
		self.suninfo.grid(row = 7, column = 0, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		self.clickinfo = tk.Label(self, text = 'Klik op de locatie van de zon waar u de vezel hebt geplaatst.\nHet systeem geeft de aanbevolen motorinstellingen.')
		self.clickinfo.grid(row = 8, column = 0, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		
class Student_Eng(Page):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)		
		#Row 0
		self.langbutton = tk.Button(self, text = 'NED',
					command = lambda: controller.show_frame(Student_Ned))
		self.langbutton.grid(row = 0, column = 0, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2)
		self.quitbutton = tk.Button(self, text="Close",
					command = lambda: Quit(self), bg='red')
		self.quitbutton.grid(row = 0, column = 4, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2)
		#Row 2 & 3
		self.invoerlabel = tk.Label(self, text = 'Specify integration time:')
		self.invoerlabel.grid(row = 2, column = 4, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		self.Invoer = tk.Entry(self)
		self.Invoer.grid(row = 3, column = 4)

		self.invoernaam = tk.Label(self, text = 'Specify file name:')
		self.invoernaam.grid(row = 2, column = 5, padx = 5, pady = 2.5, sticky = 'nesw', columnspan = 1)
		self.naam = tk.Entry(self)
		self.naam.grid(row = 3, column = 5)
		# Row 3	
		self.updatesun = tk.Button(self, text = 'Update the Sun', command = lambda: RetrieveSun(self,4))
		self.updatesun.grid(row = 3, column = 0, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		self.recordbutton = tk.Button(self, text = 'Record', command = lambda: proggel.main(eval(self.Invoer.get()), self.naam.get()))
		self.recordbutton.grid(row = 3, column = 2, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		self.plotbutton = tk.Button(self, text="Plot", command = lambda: plotmeasurement(self,5))
		self.plotbutton.grid(row = 3, column = 3, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		
		#Row 4, Reference Sun
		fig4 = p.figure(figsize = (3,2.5))
		canvas = FigureCanvasTkAgg(fig4, self)
		canvas.get_tk_widget().grid(row = 4, column = 0, padx = 5, sticky = 'news')
		fig4.canvas.mpl_connect('button_press_event',lambda event: printcoords(event))	
		#Row 4, Frame for measurement image
		fig5 = p.figure(figsize = (3,2.5))
		canvas5 = FigureCanvasTkAgg(fig5, self)
		canvas5.get_tk_widget().grid(row = 4, column = 2, padx = 5, sticky = 'news', columnspan = 2)
		toolbar4 = NavigationToolbar2TkAgg(canvas5, self)
		toolbar4.update()
		toolbar4.grid(row = 5, column = 2, sticky = 'news', columnspan = 2)
		#Row 4, Frame for measurement data collapsed
		fig6 = p.figure(figsize = (3,2.5))
		canvas6 = FigureCanvasTkAgg(fig6, self)
		canvas6.get_tk_widget().grid(row = 4, column = 4, padx = 5, sticky = 'news', columnspan = 2)
		toolbar5 = NavigationToolbar2TkAgg(canvas6, self)
		toolbar5.update()
		toolbar5.grid(row = 5, column = 4, sticky = 'news', columnspan = 2)
		
		#Row 7, 8 Info
		self.suninfo = tk.Label(self, text = 'The rotated Sun as seen on the screen, the blue line is the equator.')
		self.suninfo.grid(row = 7, column = 0, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		self.clickinfo = tk.Label(self, text = 'Click on the location of the Sun where you have placed the fibre.\nThe system will provide recommended motor settings.')
		self.clickinfo.grid(row = 8, column = 0, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)

##########################     START LAMBDA FUNCTIONS     ##########################

def plotmeasurement(self,fignum):	
	p.figure(fignum)
	p.clf()		
	raw_data=pyfits.getdata(self.naam.get()+'.fit')
	dark_data=pyfits.getdata(self.naam.get()+'_DarkCurrent.fit')
	dark_data =dark_data.astype(np.int16) #Deze twee .astype() handelingen zijn nodig om te data in het correcte format te zetten
	raw_data =raw_data.astype(np.int16)   #Negatieve waarden worden anders onjuist behandeld
	data=raw_data - dark_data
	data=data.T
	p.imshow(data)#, interpolation='nearest', origin='upper')

	p.gcf().canvas.draw()
	p.figure(fignum+1)
	p.clf()
	fs.readdata(data)
	p.gcf().canvas.draw()

def printcoords(event):
	#Function to retrieve coordinates from button click event by user.
	#Example of implementation:
	#	fig9.canvas.mpl_connect('button_press_event',lambda event: printcoords(event))
	# must define which figure (here, fig9) we want to retrieve input from	

	# mouseclick event coordinates (dx,dy)
	dx=event.x
	dy=event.y
	#make reference grid of fibre alignment values
	#projected cone of light is not centred on screen. Top of sun is not angled, bottom of sun is angled by ~11.6 degrees. Need to calculate angle of correction depending on 
	cen=512/2
	xpoint=dx-cen
	ypoint=dy-cen
	radius=np.sqrt(xpoint**2 + ypoint**2)
	sol_rad=radius*(695700/300)
	theta=np.sin(xpoint/radius)
	#print (radius, theta)
	dtheta_dy=11.6/1024 # angle variation from top to bottom
	yang=dy*dtheta_dy
	dtheta_dx=11.6/2/1024 # angle variation from L to R
	xang=xpoint*dtheta_dx
	# determine angle of motor settings and 
	#make pop-up of what recommended settings should be given on motor
	text="Selected pixel: ("+str(dx)+","+str(dy)+"). \n\nRecommended stepper motor settings are:\nLeft motor:"+str(round(xang,4))+"mm\nRight motor:"+str(round(yang,4))+"mm.\n\nClick OK once you have entered these settings."
	tkMessageBox.showinfo("Recommended Settings:",message= text)

def RetrieveSun(self,fignum):
	#Function to retrieve current solar image from SDO webpage
	#to call, use: lambda: RetrieveSun(self,fignum) where fignum is the figure/canvas at which to display the image
	url='http://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg'
	urllib.urlretrieve(url, 'dezon.jpg')
	img=Image.open('dezon.jpg')
	projected_img=ImageOps.flip(img) #Het beeld is Noord-Zuid gespiegeld
	projected_img=ImageOps.mirror(projected_img)
	RotationAngle=24  #Beeld 24 graden geroteerd tenopzichte van loodrecht (naar links kijkend vanaf projectie scherm, dus naar rechts kijkend NAAR scherm)!!
	#Daar komt ook bij dat de Aarde ten opzichte van de zon 23.43707 graden gedraaid is
	#dit varieert van -23.43707 graden naar +23.43707 graden gedurende het jaar
	#sin met 0 op summer solstice (21 juni) en op winter solstice (21 december)
	#Wanneer is het 0?
		
	x=np.arange(0,365.25,0.25)
	y=[23.43707*np.sin(2*np.pi*(i*360.0/365.0 - 172*360.0/365.0)) for i in x] #in degrees
	day_of_year=datetime.datetime.now().timetuple().tm_yday
	extra_angle=y[day_of_year]
	#dec=23.45*np.pi/180 * np.sin(2*np.pi*((284+day_of_year)/36.25)) 	
	#aantal uur tot/vanaf plaatselijke noon
	now=datetime.datetime.now()
	today=now.date()
	noon=datetime.time(hour=12)
	noon_today=datetime.datetime.combine(today, noon)
	diff=now - noon_today
	minutes, seconds=divmod(diff.total_seconds(), 60)
	hours=minutes/60.0 + seconds/360.0
	degrees=hours*15.0
	RotationAngle=RotationAngle - degrees - extra_angle
	#print('Hour angle degrees:', degrees)
	#print('Angle based on day of the year:', extra_angle)
	#print('Rotation angle:', RotationAngle)
	img2=projected_img.rotate(-RotationAngle)

	p.figure(fignum)
	p.clf()	
	centerX, centerY=512, 512		
	xdisp=512.0*np.cos(np.radians(RotationAngle))
	ydisp=512.0*np.sin(np.radians(RotationAngle))
	p.gca().invert_yaxis()

	p.plot([centerX-xdisp, centerX+xdisp], [centerY-ydisp,centerY+ydisp])
	p.imshow(img2)
	p.axis('off')
	p.gcf().canvas.draw()

def Quit(self):
	#Function to shutdown program properly
	root.quit()
	root.destroy()	

##########################      END LAMBDA FUNCTIONS      ##########################
		
if __name__ == "__main__":
	root = tk.Tk()	
	app = HelioGUI(root)
	app.pack(side = 'top', fill = 'both', expand = True)
	#root.wm_geometry('1400x900')
	root.attributes("-fullscreen", True)

	root.mainloop()
	
	