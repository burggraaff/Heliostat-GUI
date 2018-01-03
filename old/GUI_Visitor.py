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

from PIL import Image, ImageTk
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

		for F in (Page1,Page2,Page3,Page4,Page5):
			frame = F(self.container, self)
			self.frames[F] = frame
			frame.grid(row = 0, column = 0, sticky = tk.NSEW)
			self.container.grid_rowconfigure(1, weight = 1)
			self.container.grid_columnconfigure(1, weight = 1)
		
		#self.xang = tk.StringVar()
		#self.yang = tk.StringVar()
		self.show_frame(Page1)	
		
	def show_frame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()				#brings the frame to the top for the user to see
		
class Page1(Page):
	
	def __init__(self, parent, controller):
	
		tk.Frame.__init__(self, parent)
		# Create a Tkinter variable
		tkvar = StringVar(root)
 
		# Dictionary with options
		choices = { 'NED','ENG','DEU','FRA'}
		tkvar.set('ENG') # set the default option
 
		langMenu = tk.OptionMenu(self, tkvar, *choices)
		langMenu.grid(row = 0, column =0, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
		
		# on change dropdown value
		def change_dropdown(*args):
			print( tkvar.get() )
 
		# link function to change dropdown
		tkvar.trace('w', change_dropdown)
		
		label = tk.Label(self, text="""1. Move the Device""", font = LABEL_FONT)
		label.grid(row = 0, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		
		quitbutton = tk.Button(self, text = 'Close',
							command = lambda: Quit(self), font = LARGE_FONT, bg='red')
		quitbutton.grid(row = 0, column = 3, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
						
		instruct = tk.Label(self, text = 'Move the fibre somewhere on the Sun \nby squeezing the handles to release the device')
		instruct.grid(row = 1, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)

		fig1 = p.figure(figsize = (3,3))
		canvas1 = FigureCanvasTkAgg(fig1, self)
		canvas1.get_tk_widget().grid(row = 2, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		img=Image.open('Move_handheld.jpg')
		p.figure(1)
		p.clf()	
		p.imshow(img)
		p.axis('off')
		p.gcf().canvas.draw()
		
		nextbutton = tk.Button(self, text = 'Next->', 
							command = lambda: controller.show_frame(Page2), font = LARGE_FONT)
		nextbutton.grid(row = 4, column = 3, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
		
		col_count, row_count = self.grid_size()
		for row in xrange(row_count):
			self.grid_rowconfigure(row, weight = 1)
		
		for col in xrange(col_count):
			self.grid_columnconfigure(col, weight = 1)

		
class Page2(Page):
	
	def __init__(self, parent, controller):
	
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="""2. Indicate location of the fibre""", font = LABEL_FONT)
		label.grid(row = 0, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		
		quitbutton = tk.Button(self, text = 'Close',
							command = lambda: Quit(self), font = LARGE_FONT, bg='red')
		quitbutton.grid(row = 0, column = 3, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
								
		button3 = tk.Button(self, text = 'Click to Display the Sun', command = lambda: RetrieveSun(self,2), font = LARGE_FONT)
		button3.grid(row = 1, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		
		instruct = tk.Label(self, text = 'After the Sun displays,\nclick on the location where you placed\nthe handheld device on the Sun')
		instruct.grid(row = 2, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)

		fig2 = p.figure(figsize = (3,3))
		canvas2 = FigureCanvasTkAgg(fig2, self)
		canvas2.get_tk_widget().grid(row = 3, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		fig2.canvas.mpl_connect('button_press_event',lambda event: printcoords(event))	
		
		backbutton = tk.Button(self, text = '<-Back', 
							command = lambda: controller.show_frame(Page1), font = LARGE_FONT)
		backbutton.grid(row = 4, column = 0, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
		
		nextbutton = tk.Button(self, text = 'Next->', 
							command = lambda: controller.show_frame(Page3), font = LARGE_FONT)
		nextbutton.grid(row = 4, column = 3, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)

	def Quit(self):
		root.quit()
		root.destroy()
		
class Page3(Page):
	
	def __init__(self, parent, controller):
	
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="""3. Set the Motors""", font = LABEL_FONT)
		label.grid(row = 0, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		
		quitbutton = tk.Button(self, text = 'Close',
							command = lambda: Quit(self), font = LARGE_FONT, bg='red')
		quitbutton.grid(row = 0, column = 3, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
						
		instruct = tk.Label(self, text = 'Make sure you have entered the recommended settings \nin the left and right motors')
		instruct.grid(row = 1, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)

		fig3 = p.figure(figsize = (3,3))
		canvas3 = FigureCanvasTkAgg(fig3, self)
		canvas3.get_tk_widget().grid(row = 2, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		
		img=Image.open('Motor_display.jpg')
		p.figure(3)
		p.clf()	
		p.imshow(img)
		p.axis('off')
		p.gcf().canvas.draw()
		#print(self.xang)
		
		ltext="Left Motor:"#+self.xang.get()
		left = tk.Label(self, text = ltext)
		left.grid(row = 3, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
		rtext="Right Motor:"#+self.yang.get()
		right = tk.Label(self, text = rtext)
		right.grid(row = 3, column = 2, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
		
		backbutton = tk.Button(self, text = '<-Back', 
							command = lambda: controller.show_frame(Page2), font = LARGE_FONT)
		backbutton.grid(row = 4, column = 0, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
		
		nextbutton = tk.Button(self, text = 'Next->', 
							command = lambda: controller.show_frame(Page4), font = LARGE_FONT)
		nextbutton.grid(row = 4, column = 3, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
		
class Page4(Page):
	
	def __init__(self, parent, controller):
	
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="""4. Record Data""", font = LABEL_FONT)
		label.grid(row = 0, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		
		quitbutton = tk.Button(self, text = 'Close',
							command = lambda: Quit(self), font = LARGE_FONT, bg='red')
		quitbutton.grid(row = 0, column = 3, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
						
		instruct = tk.Label(self, text = 'Provide an intergration time and file name')
		instruct.grid(row = 1, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		
		self.invoerlabel = tk.Label(self, text = 'Integration Time:')
		self.invoerlabel.grid(row = 2, column = 1, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 1)
		self.Invoer = tk.Entry(self)
		self.Invoer.grid(row = 3, column = 1)
		
		self.invoernaam = tk.Label(self, text = 'File Name:')
		self.invoernaam.grid(row = 2, column = 2, padx = 5, pady = 2.5, sticky = 'nesw', columnspan = 1)
		self.naam = tk.Entry(self)
		self.naam.grid(row = 3, column = 2)
		
		button3 = tk.Button(self, text = 'Record', command = lambda: proggel.main(eval(self.Invoer.get()), self.naam.get()), font = LARGE_FONT)
		button3.grid(row = 4, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)

		backbutton = tk.Button(self, text = '<-Back', 
							command = lambda: controller.show_frame(Page3), font = LARGE_FONT)
		backbutton.grid(row = 5, column = 0, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
		
		nextbutton = tk.Button(self, text = 'Next->', 
							command = lambda: controller.show_frame(Page5), font = LARGE_FONT)
		nextbutton.grid(row = 5, column = 3, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)

		
class Page5(Page):
	
	def __init__(self, parent, controller):
	
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="""5. Plot Data""", font = LABEL_FONT)
		label.grid(row = 0, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		
		quitbutton = tk.Button(self, text = 'Close',
							command = lambda: Quit(self), font = LARGE_FONT, bg='red')
		quitbutton.grid(row = 0, column = 3, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
						
		instruct = tk.Label(self, text = 'Show the data you just took!')
		instruct.grid(row = 1, column = 1, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
			
		self.plotbutton = tk.Button(self, text="Plot!", command = lambda: plotmeasurement(self,4))
		self.plotbutton.grid(row = 2, column = 1, padx = 5, pady = 2.5, sticky ='nesw', columnspan = 2)

		fig4 = p.figure(figsize = (3,3))
		canvas4 = FigureCanvasTkAgg(fig4, self)
		canvas4.get_tk_widget().grid(row = 3, column = 0, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		fig5 = p.figure(figsize = (3,3))
		canvas5 = FigureCanvasTkAgg(fig5, self)
		canvas5.get_tk_widget().grid(row = 3, column = 2, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 2)
		
		backbutton = tk.Button(self, text = '<-Back', 
							command = lambda: controller.show_frame(Page4), font = LARGE_FONT)
		backbutton.grid(row = 5, column = 0, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
		
		nextbutton = tk.Button(self, text = 'Next->', 
							command = print('next'), font = LARGE_FONT)
		nextbutton.grid(row = 5, column = 3, padx = 5, pady = 2.5, sticky = tk.NSEW, columnspan = 1)
		
		
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
	ya=dy*dtheta_dy
	dtheta_dx=11.6/2/1024 # angle variation from L to R
	xa=xpoint*dtheta_dx
	# determine angle of motor settings and 
	#make pop-up of what recommended settings should be given on motor
	text="Selected pixel: ("+str(dx)+","+str(dy)+"). \n\nRecommended stepper motor settings are:\nLeft motor:"+str(round(xa,4))+"mm\nRight motor:"+str(round(ya,4))+"mm.\n\nClick OK once you have entered these settings."
	tkMessageBox.showinfo("Recommended Settings:",message= text)
	#self.xang.set(str(round(xa,4)))
	#self.yang.set(str(round(ya,4)))
	#print(self.xang)
	
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
	root.wm_geometry('1000x500')
	#root.wm_geometry('1400x900')
	#root.attributes("-fullscreen", True)

	root.mainloop()
	