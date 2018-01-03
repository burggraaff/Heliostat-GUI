#!/usr/bin/python

#			Tutorial from:
#https://pythonprogramming.net/plotting-live-bitcoin-price-data-tkinter-matplotlib/

#Tuesday, Nov 21:
#Edited toolbar(line~430), toolbar2(line~460), toolbar3(line~487),toolbar4(line~500) to correct use of pack & grid at same time
#Disabled all calls to proggel, doesn't work without connection to camera or file sbig
#Changed buttons to English, as compared to GUI_copy.py

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

from tkinter import messagebox

#hiermee besturen we de camera
#sys.path.insert(0, '../sbig')
#import proggel as proggel

import tkFont

LARGE_FONT= ('TkDefaultFont', 14)
LABEL_FONT=('TkDefaultFont', 16)

class Page(tk.Frame):
	def __init__(self, *args, **kwargs):
		tk.Frame.__init__(self, *args, **kwargs)

	def show(self):
		self.lift()

class HelioGUI(tk.Frame):
	#this is a method, init will always run when class is called upon
	#args are parameters, kwargs dictionaries
	def __init__(self, parent, *args, **kwargs):		
		
		tk.Frame.__init__(self, parent, *args, **kwargs)	#initialize the inherited class
		self.myParent=parent
		self.container=tk.Frame(self)				#just defining a container
		self.container.grid(row=0, column=0, sticky=tk.NSEW)
		self.myParent.grid_rowconfigure(0, weight=1)
		self.myParent.grid_columnconfigure(0, weight=1)	
		
		
		self.frames={} #empty dictionary		
		#frame=BTCe_Page(container, self)
		#self.frames[BTCe_Page]=frame
		#frame.grid(row=0, column=0, sticky='nsew')

		for F in (Start_Page_Ned, Start_Page_Eng, Visitor_Page_Ned, Visitor_Page_Eng, Student_Page_Ned, Student_Page_Eng):
			frame=F(self.container, self)
			self.frames[F]=frame
			frame.grid(row=0, column=0, sticky=tk.NSEW)
			self.container.grid_rowconfigure(1, weight=1)
			self.container.grid_columnconfigure(1, weight=1)
			
			col_count, row_count=frame.grid_size()
			#print(col_count, row_count)
			for row in xrange(row_count):
				frame.grid_rowconfigure(row, weight=1)
		
			for col in xrange(col_count):
				frame.grid_columnconfigure(col, weight=1)
			
		self.show_frame(Start_Page_Ned)	
		
	def show_frame(self, cont):
		frame=self.frames[cont]
		frame.tkraise()		#brings the frame to the top for the user to see
		
class Start_Page_Ned(Page):
	#The Start Page (in Dutch)
	def __init__(self, parent, controller):
	
		tk.Frame.__init__(self, parent)

		label=tk.Label(self, text='GUI voor de bediening van de spectrograaf en het plotten van het spectrum van de Zon!', font=LABEL_FONT)
		label.grid(row=0, column=2, padx=5, pady=2.5, sticky=tk.NSEW, columnspan=2)
		
		#Language button
		imgpath='UK_flag.jpg'	
		self.ukflag=PhotoImage(file=imgpath)
		self.ukflag=self.ukflag.zoom(5) #rescale to smaller
		self.ukflag=self.ukflag.subsample(60) #rescale to smaller (original 1200x600)
		button_eng=tk.Button(self,image=self.ukflag,command=lambda: controller.show_frame(Start_Page_Eng))
		button_eng.grid(row=0, column=0, padx=5, pady=2.5, sticky=tk.NSEW)
		#Visitor screen button
		button=tk.Button(self, text= 'Bezoekersscherm', 
							command= lambda: controller.show_frame(Visitor_Page_Ned), font=LARGE_FONT)
		button.grid(row=1, column=2, padx=5, pady=2.5, sticky=tk.NSEW, columnspan=2)
		#Student screen button
		button1=tk.Button(self, text= 'Studentenscherm', 
							command= lambda: controller.show_frame(Student_Page_Ned), font=LARGE_FONT)
		button1.grid(row=2, column=2, padx=5, pady=2.5, sticky=tk.NSEW, columnspan=2)
		#Button to plot current image of the Sun				
		button3=tk.Button(self, text= 'Update de Zon!', 
							command= lambda: RetrieveSun(self,1), font=LARGE_FONT)
		button3.grid(row=3, column=2, padx=5, pady=2.5, sticky=tk.NSEW, columnspan=2)
		#Updates the sun after 15 minutes (900 seconds), frquency of SDO website updates
		self.after(900*1000, lambda: RetrieveSun(self,1) )
		#Quit button
		button2=tk.Button(self, text='Afsluiten',font=LARGE_FONT,
					command=lambda: Quit(self),bg='red')
		button2.grid(row=0, column=6, padx=5, pady=2.5, sticky=tk.NSEW, columnspan=1)

		#Figure for displaying Sun
		fig1=p.figure(figsize=(7,7))
		canvas1=FigureCanvasTkAgg(fig1, self)
		canvas1.get_tk_widget().grid(row=5, column=2, padx=5, pady=2.5, sticky=tk.NSEW, columnspan=2)
		
		col_count, row_count=self.grid_size()
		print(col_count, row_count)
		for row in xrange(row_count):
			self.grid_rowconfigure(row, weight=1)
		
		for col in xrange(col_count):
			self.grid_columnconfigure(col, weight=1)


class Start_Page_Eng(Page):
	#Start Page in English
	def __init__(self, parent, controller):
		
		tk.Frame.__init__(self, parent)

		label=tk.Label(self, text='GUI for operating the spectrograph and plotting the spectrum of the Sun', font=LABEL_FONT)
		label.grid(row=0, column=2, padx=5, pady=2.5, sticky=tk.NSEW, columnspan=2)
		
		#Language button
		imgpath='NL_flag.jpg'
		self.nlflag=PhotoImage(file=imgpath)
		self.nlflag=self.nlflag.zoom(5) #rescale to smaller
		self.nlflag=self.nlflag.subsample(60) #rescale to smaller (original 900x600)
		button_nl=tk.Button(self,image=self.nlflag,command=lambda: controller.show_frame(Start_Page_Ned))
		button_nl.grid(row=0, column=0, padx=5, pady=2.5, sticky=tk.NSEW)
		#Visitor screen button
		button=tk.Button(self, text='Visitors Screen', 
				 command=lambda: controller.show_frame(Visitor_Page_Eng), font=LARGE_FONT)
		button.grid(row=1, column=2, padx=5, pady=2.5, sticky=tk.NSEW, columnspan=2)
		#Student screen button
		button1=tk.Button(self, text='Student Screen', 
				  command=lambda: controller.show_frame(Student_Page_Eng), font=LARGE_FONT)
		button1.grid(row=2, column=2, padx=5, pady=2.5, sticky=tk.NSEW, columnspan=2)
		#Button to plot current image of the Sun			
		button3=tk.Button(self, text='Display Solar Orientation', command=lambda: RetrieveSun(self,2), font=LARGE_FONT)
		button3.grid(row=3, column=2, padx=5, pady=2.5, sticky=tk.NSEW, columnspan=2)
		#Updates the sun after 15 minutes (900 seconds), frquency of SDO website updates
		self.after(900*1000, lambda: RetrieveSun(self,2) )	
		#Quit button
		button2=tk.Button(self,text='CLOSE',command= lambda: Quit(self), bg='red',font=LARGE_FONT)
		button2.grid(row=0, column=6, padx=5, pady=2.5, sticky=tk.NSEW, columnspan=1)

		#Figure for displaying Sun
		fig2=p.figure(figsize=(7,7))
		canvas=FigureCanvasTkAgg(fig2, self)
		canvas.get_tk_widget().grid(row=5, column=2, padx=5, pady=2.5, sticky=tk.NSEW, columnspan=2)
		
		col_count, row_count=self.grid_size()
		print(col_count, row_count)
		for row in xrange(row_count):
			self.grid_rowconfigure(row, weight=1)
		
		for col in xrange(col_count):
			self.grid_columnconfigure(col, weight=1)

class Visitor_Page_Ned(Page):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		##########################     START HEADER     ##########################
		#Language button
		imgpath='UK_flag.jpg'	
		self.ukflag=PhotoImage(file=imgpath)
		self.ukflag=self.ukflag.zoom(5) #rescale to smaller
		self.ukflag=self.ukflag.subsample(60) #rescale to smaller (original 1200x600)
		button_eng=tk.Button(self,image=self.ukflag,command=lambda: controller.show_frame(Visitor_Page_Eng))
		button_eng.grid(row=0, column=0, padx=5, pady=2.5, sticky=tk.NSEW)
		#Back to home screen button
		self.begin=tk.Button(self, text= 'Terug naar Beginscherm',font=LARGE_FONT,
					command=lambda: controller.show_frame(Start_Page_Ned))
		self.begin.grid(row= 0, column= 1, padx= 5, pady= 2.5, sticky= tk.NSEW, columnspan= 2)
		#Student screen button
		self.student=tk.Button(self, text= 'Studentenscherm',font=LARGE_FONT,
					command=lambda: controller.show_frame(Student_Page_Ned))
		self.student.grid(row= 0, column= 3, padx= 5, pady= 2.5, sticky='nesw', columnspan= 2)
		#Quit button
		self.afsluiten=tk.Button(self,text='Afsluiten',font=LARGE_FONT,
					command=lambda: Quit(self),bg='red')
		self.afsluiten.grid(row= 0, column= 6, padx= 5, pady= 2.5, sticky='nesw', columnspan= 1)
		##########################      END HEADER      ##########################

		self.label=tk.Label(self,text='Deze pagina is nog niet gemaakt/This page is not yet made')
		self.label.grid(row= 1, column= 0, padx= 5, pady= 2.5, sticky= tk.NSEW)

class Visitor_Page_Eng(Page):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		##########################     START HEADER     ##########################
		#Language button
		imgpath='NL_flag.jpg'
		self.nlflag=PhotoImage(file=imgpath)
		self.nlflag=self.nlflag.zoom(5) #rescale to smaller
		self.nlflag=self.nlflag.subsample(60) #rescale to smaller (original 900x600)
		button_nl=tk.Button(self,image=self.nlflag,command=lambda: controller.show_frame(Visitor_Page_Ned))
		button_nl.grid(row=0, column=0, padx=5, pady=2.5, sticky=tk.NSEW)
		#Back to home screen button
		self.begin=tk.Button(self, text= 'Back to Home Screen',font=LARGE_FONT,
					command=lambda: controller.show_frame(Start_Page_Eng))
		self.begin.grid(row= 0, column= 1, padx= 5, pady= 2.5, sticky= tk.NSEW, columnspan= 2)
		#Student screen button
		self.student=tk.Button(self, text= 'To Student Screen',font=LARGE_FONT,
					command=lambda: controller.show_frame(Student_Page_Eng))
		self.student.grid(row= 0, column= 3, padx= 5, pady= 2.5, sticky='nesw', columnspan= 2)
		#Quit button
		self.afsluiten=tk.Button(self,text='CLOSE',font=LARGE_FONT,
					command=lambda: Quit(self),bg='red')
		self.afsluiten.grid(row= 0, column= 6, padx= 5, pady= 2.5, sticky='nesw', columnspan= 1)
		##########################      END HEADER      ##########################

		#Show how to move fibre
		self.fibre=tk.Button(self, text= '1. Place the fibre somewhere on the Sun', command=self.DisplayFibreMove)
		self.fibre.grid(row= 1, column= 1, padx= 5, pady= 2.5, sticky='nesw', columnspan= 2)
		#Update the Sun!
		self.zon=tk.Button(self, text= '2. Click on the Sun where you have placed the fibre', command=lambda: RetrieveSun(self,4))
		self.zon.grid(row= 1, column= 3, padx= 5, pady= 2.5, sticky='nesw', columnspan= 2)
		#Select where the fibre has been moved to
		self.motor=tk.Button(self, text= '3. Set the Left and Right Motors', command= self.DisplayMotorMove)
		self.motor.grid(row= 1, column= 5, padx= 5, pady= 2.5, sticky='nesw', columnspan= 2)
		#Recording!
		#self.NeemOpname=tk.Button(self, text='Opname!', command=lambda: proggel.main(eval('0.04'), 'Bezoekers1'))
		self.NeemOpname=tk.Button(self, text='4. Record Data', command=print('NeemOpname'))
		self.NeemOpname.grid(row= 4, column= 1, padx= 5, pady= 2.5, sticky='nesw', columnspan= 2)
		#Plot!
		self.plot=tk.Button(self, text='5. Plot Data', command=lambda: plotmeasurement(self,6))
		self.plot.grid(row= 4, column= 3, padx= 5, pady= 2.5, sticky='nesw', columnspan= 2)
		
		fig3=p.figure(figsize=(4,4))
		canvas3=FigureCanvasTkAgg(fig3, self)
		canvas3.get_tk_widget().grid(row=2, column=1, padx=5, sticky='nesw', columnspan=2)	
		
		fig4=p.figure(figsize=(6,4))
		canvas4=FigureCanvasTkAgg(fig4, self)
		canvas4.get_tk_widget().grid(row=2, column=3, padx=5, pady= 2.5, sticky='nesw', columnspan=2)
		#Updates the sun every 15 minutes (900 seconds) based on SDOs update frequency
		self.after(900*1000,  lambda: RetrieveSun(self,4))		
		#What to do when position on Sun is clicked 
		fig4.canvas.mpl_connect('button_press_event',lambda event: printcoords(event))	

		fig5=p.figure(figsize=(6,4))
		canvas5=FigureCanvasTkAgg(fig5, self)
		canvas5.get_tk_widget().grid(row=2, column=5, padx=5, pady=2.5, sticky='nesw', columnspan=2)
		
		#Recording!
		#self.NeemOpname1=tk.Button(self, text='Opname!', command=lambda: proggel.main(eval('0.04'), 'Bezoekers2'))
		"""
		self.NeemOpname1=tk.Button(self, text='Record Data', command=print('NeemOpname1'))
		self.NeemOpname1.grid(row=3, column=3, padx=5, pady=2.5, sticky ='nesw', columnspan=2)		
		#Plot!
		self.plot1=tk.Button(self, text='Plot Data', command=self.secondmeasurement)
		self.plot1.grid(row=3, column=5, padx=5, pady=2.5, sticky ='nesw', columnspan=2)
		"""	
		#The rotated Sun as seen on the screen, the blue line is the equator.
		self.gedraaidezon=tk.Label(self, text='The Sun\'s current orientation, as seen on the screen. The blue line is the equator.')
		self.gedraaidezon.grid(row=3, column=2, padx=5, pady=2.5, sticky ='nesw', columnspan=1)

		fig6=p.figure(figsize=(6,4))
		canvas6=FigureCanvasTkAgg(fig6, self)
		canvas6.get_tk_widget().grid(row=5, column=1, padx=5, pady=2.5, sticky='nesw', columnspan=2)
		
		fig7=p.figure(figsize=(6,4))
		canvas7=FigureCanvasTkAgg(fig7, self)
		canvas7.get_tk_widget().grid(row=5, column=3, padx=5, pady=2.5, sticky='nesw', columnspan=2)

		fig8=p.figure(figsize=(6,4))
		canvas8=FigureCanvasTkAgg(fig8, self)
		canvas8.get_tk_widget().grid(row=5, column=5, padx=5, pady=2.5, sticky='nesw', columnspan=2)

	def DisplayFibreMove(self):
		#show gif of movement of fibre
		handheld=Image.open('Move_handheld.jpg')
		p.figure(3)
		p.clf()
		p.imshow(handheld)
		p.gcf().canvas.draw()

	def DisplayMotorMove(self):
		#show gif of movement of fibre
		handheld=Image.open('Motor_display.jpg')
		p.figure(5)
		p.clf()
		p.imshow(handheld)
		p.gcf().canvas.draw()

class Student_Page_Ned(Page):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		##########################     START HEADER     ##########################
		#Language button
		imgpath='UK_flag.jpg'	
		self.ukflag=PhotoImage(file=imgpath)
		self.ukflag=self.ukflag.zoom(5) #rescale to smaller
		self.ukflag=self.ukflag.subsample(60) #rescale to smaller (original 1200x600)
		button_eng=tk.Button(self,image=self.ukflag,command=lambda: controller.show_frame(Student_Page_Eng))
		button_eng.grid(row=0, column=0, padx=5, pady=2.5, sticky=tk.NSEW)
		# Back to home screen button
		self.button2=tk.Button(self, text='Terug naar Beginscherm',font=LARGE_FONT,
					command=lambda: controller.show_frame(Start_Page_Ned))
		self.button2.grid(row=0, column=1, padx=5, pady=2.5, sticky ='nesw', columnspan=2)
		# Visitor screen button
		self.button4=tk.Button(self, text='Naar Bezoekersscherm',font=LARGE_FONT,
					command=lambda: controller.show_frame(Visitor_Page_Ned))
		self.button4.grid(row=0, column=3, padx=5, pady=2.5, sticky ='nesw', columnspan=2)
		#Quit button
		self.draw_button3=tk.Button(self, text='Afsluiten',font=LARGE_FONT,
					command=lambda: Quit(self),bg='red')
		self.draw_button3.grid(row=0, column=6, padx=5, pady=2.5, sticky ='nesw', columnspan=1)
		##########################      END HEADER      ##########################
		
		self.draw_button1=tk.Button(self, text='Update de Zon!', command=lambda: RetrieveSun(self,9))
		self.draw_button1.grid(row=3, column=1, padx=5, pady=2.5, sticky ='nesw', columnspan=1)

		#Integration time and file name settings
		self.invoerlabel=tk.Label(self, text='Geef hier de gewenste integratietijd:')
		self.invoerlabel.grid(row=2, column=5, padx=5, pady=2.5, sticky ='nesw', columnspan=1)
		self.Invoer=tk.Entry(self)
		self.Invoer.grid(row=3, column=5)
		
		self.invoernaam=tk.Label(self, text='Geef hier de gewenste bestandsnaam:')
		self.invoernaam.grid(row=2, column=6, padx=5, pady=2.5, sticky='nesw', columnspan=1)
		self.naam=tk.Entry(self)
		self.naam.grid(row=3, column=6)
		
		#self.NeemOpname=tk.Button(self, text='Opname!', command=lambda: proggel.main(eval(self.Invoer.get()), self.naam.get()))
		self.NeemOpname=tk.Button(self, text='Opname', command=print('Opname!'))
		self.NeemOpname.grid(row=3, column=3, padx=5, pady=2.5, sticky ='nesw', columnspan=1)
			
		self.draw_button=tk.Button(self, text='Plot', command=lambda: plotmeasurement(self,10))
		self.draw_button.grid(row=3, column=4, padx=5, pady=2.5, sticky ='nesw', columnspan=1)
		
		#referentie zon
		fig9=p.figure(figsize=(4,4))
		canvas9=FigureCanvasTkAgg(fig9, self)
		canvas9.get_tk_widget().grid(row=4, column=1, padx=5, sticky='news')	
		#Updates the sun every 15 minutes (900 seconds) based on SDOs update frequency
		self.after(900*1000,  lambda: RetrieveSun(self,9) )	
		
		#What to do when position on Sun is clicked 
		fig9.canvas.mpl_connect('button_press_event',lambda event: printcoords(event))	
		
		#Meting 1
		fig10=p.figure(figsize=(6,4))
		canvas10=FigureCanvasTkAgg(fig10, self)
		canvas10.get_tk_widget().grid(row=4, column=3, padx=5, sticky='news', columnspan=2)
		toolbar10_frame=Frame(self)
		toolbar10_frame.grid(row=5, column=3, sticky='news', columnspan=2)
		toolbar10=NavigationToolbar2TkAgg(canvas10, toolbar10_frame)
			
		#Meting 1
		fig11=p.figure(figsize=(6,4))
		canvas11=FigureCanvasTkAgg(fig11, self)
		canvas11.get_tk_widget().grid(row=4, column=5, padx=5, sticky='news', columnspan=2)
		toolbar11_frame=Frame(self)
		toolbar11_frame.grid(row=5, column=5, sticky='news', columnspan=2)
		toolbar11=NavigationToolbar2TkAgg(canvas11, toolbar11_frame)

		#Gedraaide zon
		self.gedraaidezon=tk.Label(self, text='De geroteerde Zon zoals te zien op het scherm, de blauwe lijn is de evenaar. \nKlik op de locatie waar u de vezel op de zon hebt geplaatst om de aanbevolen motorinstellingen op te halen.',justify=LEFT,wraplength=400)
		self.gedraaidezon.grid(row=6, column=1, padx=5, pady=2.5, sticky ='nesw', columnspan=2)	

class Student_Page_Eng(Page):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		##########################     START HEADER     ##########################
		#Language button
		imgpath='NL_flag.jpg'
		self.nlflag=PhotoImage(file=imgpath)
		self.nlflag=self.nlflag.zoom(5) #rescale to smaller
		self.nlflag=self.nlflag.subsample(60) #rescale to smaller (original 900x600)
		button_nl=tk.Button(self,image=self.nlflag,command=lambda: controller.show_frame(Student_Page_Ned))
		button_nl.grid(row=0, column=0, padx=5, pady=2.5, sticky=tk.NSEW)
		#Back to home screen button
		self.button2=tk.Button(self, text='Back to Home Screen',font=LARGE_FONT,
					command=lambda: controller.show_frame(Start_Page_Eng))
		self.button2.grid(row=0, column=1, padx=5, pady=2.5, sticky ='nesw', columnspan=2)
		#Visitor screen button
		self.button4=tk.Button(self, text='To Visitors Screen',font=LARGE_FONT,
					command=lambda: controller.show_frame(Visitor_Page_Eng))
		self.button4.grid(row=0, column=3, padx=5, pady=2.5, sticky ='nesw', columnspan=2)
		#Quit button
		self.draw_button3=tk.Button(self, text='CLOSE',font=LARGE_FONT,
					command=lambda: Quit(self),bg='red')
		self.draw_button3.grid(row=0, column=6, padx=5, pady=2.5, sticky ='nesw', columnspan=1)
		##########################      END HEADER      ##########################
		
		self.draw_button1=tk.Button(self, text='Show Solar Orientation', command=lambda: RetrieveSun(self,12))
		self.draw_button1.grid(row=4, column=1, padx=5, pady=2.5, sticky ='nesw', columnspan=1)

		#Integration time and file name settings
		self.invoerlabel=tk.Label(self, text='Integration Time:')
		self.invoerlabel.grid(row=2, column=3, padx=5, pady=2.5, sticky ='nesw', columnspan=1)
		self.Invoer=tk.Entry(self)
		self.Invoer.grid(row=2, column=4)
		
		self.invoernaam=tk.Label(self, text='File Name:')
		self.invoernaam.grid(row=3, column=3, padx=5, pady=2.5, sticky='nesw', columnspan=1)
		self.naam=tk.Entry(self)
		self.naam.grid(row=3, column=4)
		
		#self.NeemOpname=tk.Button(self, text='Opname!', command=lambda: proggel.main(eval(self.Invoer.get()), self.naam.get()))
		self.NeemOpname=tk.Button(self, text='Record Data', command=print('Opname!'))
		self.NeemOpname.grid(row=2, column=5, padx=5, pady=2.5, sticky ='nesw', columnspan=1,rowspan=2)
			
		self.draw_button=tk.Button(self, text='Plot Data', command=lambda: plotmeasurement(self,13))
		self.draw_button.grid(row=4, column=3, padx=5, pady=2.5, sticky ='nesw', columnspan=4)
		
		#referentie zon
		fig12=p.figure(figsize=(4,4))
		canvas12=FigureCanvasTkAgg(fig12, self)
		canvas12.get_tk_widget().grid(row=5, column=1, padx=5, sticky='news')	
		#Updates the sun every 15 minutes (900 seconds) based on SDOs update frequency
		self.after(900*1000,  lambda: RetrieveSun(self,12) )	
		
		#What to do when position on Sun is clicked 
		fig12.canvas.mpl_connect('button_press_event',lambda event: printcoords(event))	
		
		#Meting 1
		fig13=p.figure(figsize=(6,4))
		canvas13=FigureCanvasTkAgg(fig13, self)
		canvas13.get_tk_widget().grid(row=5, column=3, padx=5, sticky='news', columnspan=2)
		toolbar13_frame=Frame(self)
		toolbar13_frame.grid(row=6, column=3, sticky='news', columnspan=2)
		toolbar13=NavigationToolbar2TkAgg(canvas13, toolbar13_frame)
			
		#Meting 1
		fig14=p.figure(figsize=(6,4))
		canvas14=FigureCanvasTkAgg(fig14, self)
		canvas14.get_tk_widget().grid(row=5, column=5, padx=5, sticky='news', columnspan=2)
		toolbar14_frame=Frame(self)
		toolbar14_frame.grid(row=6, column=5, sticky='news', columnspan=2)
		toolbar14=NavigationToolbar2TkAgg(canvas14, toolbar14_frame)

		#Gedraaide zon
		self.gedraaidezon=tk.Label(self, text='The Sun\'s current orientation, as seen on the screen. The blue line is the equator. \nClick on the location where you have placed the fibre on the Sun to retrieve recommended motor settings.',justify=LEFT,wraplength=400)
		self.gedraaidezon.grid(row=6, column=1, padx=5, pady=2.5, sticky ='nesw', columnspan=2)	

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
	messagebox.showinfo("Recommended Settings:",message= text)

def RetrieveSun(self,fignum):
	#Function to retrieve current solar image from SDO webpage
	#to call, use: lambda: RetrieveSun(self,fignum) where fignum is the figure/canvas at which to display the image
	url='http://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg'
	urllib.urlretrieve(url, 'dezon.jpg')
	img=Image.open('dezon.jpg')
		
	#Merging the solar image with NESW-image
	bottom=Image.open('dezon.jpg')
	top=Image.open('Overlay.jpg')
	r,g,b=top.split()
	top=Image.merge('RGB',(r,g,b))
	mask=Image.merge('L', (b,))
	bottom.paste(top, (0,0), mask)
	bottom.save('samen.jpg')
	projected_img=ImageOps.flip(bottom) #Het beeld is Noord-Zuid gespiegeld
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
	print('Hour angle degrees:', degrees)
	print('Angle based on day of the year:', extra_angle)
	print('Rotation angle:', RotationAngle)
	img2=projected_img.rotate(-RotationAngle)

	p.figure(fignum)
	p.clf()	
	centerX, centerY=512, 512		
	xdisp=512.0*np.cos(np.radians(RotationAngle))
	ydisp=512.0*np.sin(np.radians(RotationAngle))
	p.xlim(0,1024)
	p.ylim(0,1024)
	p.gca().invert_yaxis()

	p.plot([centerX-xdisp, centerX+xdisp], [centerY-ydisp,centerY+ydisp])
	p.imshow(img2)
	p.gcf().canvas.draw()

def Quit(self):
	#Function to shutdown program properly
	root.quit()
	root.destroy()	

##########################      END LAMBDA FUNCTIONS      ##########################	
		
if __name__ == "__main__":
	root=tk.Tk()	
	app=HelioGUI(root)
	app.pack(side='top', fill='both', expand=True)
	root.wm_geometry('1600x900')
	#root.attributes("-fullscreen", True)
	
	root.mainloop()
	
	
