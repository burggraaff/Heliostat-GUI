"""
GUI for aligning the fibre to easily gather 'known' positions that work.
These are then saved into a table, to which a fit is made either during
run time of the main script or in this script.
(which option we use is TBD)
"""

from __future__ import print_function
import gui
from gui import tk, LABEL_FONT
from gui.fibre import Aligner
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

class Page1(gui.Page):
    def __init__(self, parent, controller):
        gui.Page.__init__(self, parent, controller, langfile = "student")

        self.title = gui.tk.Label(self, text = "STUDENT SCREEN", font = gui.LABEL_FONT)
        self.title.grid(row = 0, column = 1, columnspan = 10, stick = "news")

        self.align = FitFrame(parent=self, controller=self.controller)
        self.align.grid(row = 1, column = 1, columnspan = 10, sticky = "news")

    def end(self):
        self.align.end()
        gui.Page.end(self)

class FitFrame(tk.Frame):
    """
    Object that aids in aligning the fibre
    """
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialises AlignFrame object

        Parameters
        ----------
        self: self

        parent: parent frame, to draw this one in
        controller: controller frame, that controls e.g. timing
        """
        self.parent = parent
        self.controller = controller
        tk.Frame.__init__(self, self.parent, *args, **kwargs)
        self.x = self.y = -9999.9999
        self.fx = self.fy = -1
        self.l = 0

        self.aligner = Aligner()

        self.b_inte = tk.Button(self, text = "UPDATE", font = LABEL_FONT, height = 2, width = 10, command = self.update)
        self.b_inte.grid(row = 0, column = 4, sticky = "news")
        self.b_plot = tk.Button(self, text = "PHOTO", font = LABEL_FONT, height = 2, width = 10, command = self.photo)
        self.b_plot.grid(row = 1, column = 4, sticky = "news")
        self.b_find = tk.Button(self, text = "FIND LEDS", font = LABEL_FONT, height = 2, width = 10, command = self.find_leds)
        self.b_find.grid(row = 2, column = 4, sticky = "news")
        self.b_opti = tk.Button(self, text = "OPTIMISE", font = LABEL_FONT, height = 2, width = 10, command = self.optimise)
        self.b_opti.grid(row = 3, column = 4, sticky = "news")
        self.b_save = tk.Button(self, text = "SAVE", font = LABEL_FONT, height = 2, width = 10, command = self.save)
        self.b_save.grid(row = 4, column = 4, sticky = "news")

        self.fig = plt.figure(figsize=(7,5), facecolor = "none", tight_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=2)

        self.fig_xx = plt.figure(figsize=(4,4), facecolor = "none", tight_layout=True)
        self.canvas_xx = FigureCanvasTkAgg(self.fig_xx, self)
        self.canvas_xx.get_tk_widget().grid(row=0, column=1, rowspan=2)

        self.fig_yy = plt.figure(figsize=(4,4), facecolor = "none", tight_layout=True)
        self.canvas_yy = FigureCanvasTkAgg(self.fig_yy, self)
        self.canvas_yy.get_tk_widget().grid(row=3, column=1, rowspan=2)

        self.fig_x = plt.figure(figsize=(4,4), facecolor="none", tight_layout=True)
        self.canvas_x = FigureCanvasTkAgg(self.fig_x, self)
        self.canvas_x.get_tk_widget().grid(row=0, column=2, rowspan=2)

        self.fig_y = plt.figure(figsize=(4,4), facecolor="none", tight_layout=True)
        self.canvas_y = FigureCanvasTkAgg(self.fig_y, self)
        self.canvas_y.get_tk_widget().grid(row=3, column=2, rowspan=2)

        self.f = "{0}: {1:+.4f}" # format to print values in
        self.indicator_x = tk.Label(self, text = self.f.format("X", self.x), font = LABEL_FONT)
        self.indicator_x.grid(row = 0, column = 3, sticky = "w")
        self.indicator_y = tk.Label(self, text = self.f.format("Y", self.y), font = LABEL_FONT)
        self.indicator_y.grid(row = 1, column = 3, sticky = "w")
        self.indicator_f = tk.Label(self, text = "F: (-1, -1)", font = LABEL_FONT)
        self.indicator_f.grid(row = 2, column = 3, sticky = "w")
        self.indicator_l = tk.Label(self, text = "L: 00000", font = LABEL_FONT)
        self.indicator_l.grid(row = 3, column = 3, sticky = "w")

    def end(self):
        """
        Gracefully exit
        """
        if self.aligner is not None:
            self.aligner.end()

    def update(self):
        self.x, self.y = self.aligner.get_current_positions()
        self.fx, self.fy = self.aligner.get_fibre_position()
        self.indicator_x["text"] = self.f.format("X", self.x)
        self.indicator_y["text"] = self.f.format("Y", self.y)
        self.indicator_f["text"] = "F: ({0:.0f}, {1:.0f})".format(self.fx, self.fy)
        self.indicator_l["text"] = "L: {0}".format(self.l)

    def photo(self):
        """
        Take and plot an image from the LED camera.
        """
        self.image = self.aligner.led_camera.led_image()
        self.plot()

    def find_leds(self):
        """
        Find the LEDs in the latest image from the LED camera.
        """
        self.aligner.find_LEDs(self.image)
        self.update()
        self.plot()

    def optimise(self):
        for j in range(5):
            self.l = self.aligner.intensity()
            self.update()

    def save(self):
        self.update()
        table = np.loadtxt("static/fibre_positions.txt")
        new_row = np.array([self.fx, self.fy, self.x, self.y])
        table = np.vstack((table, new_row))
        np.savetxt("static/fibre_positions.txt", table, fmt="%.4f")
        print("Saved!")
        for i, f in enumerate([self.fig_x, self.fig_y]):
            ax = f.gca()
            ax.clear()
            ax.scatter(table[:,0], table[:,1], c=table[:,i+2], vmin=-0.15, vmax=1.8, s=35)
            ax.set_xlim(0, 1280)
            ax.set_ylim(1024, 0)
            f.canvas.draw()
        for i, f in enumerate([self.fig_xx, self.fig_yy]):
            ax = f.gca()
            ax.clear()
            ax.scatter(table[:,i], table[:,i+2])
            ax.set_xlim(0, 1024 + i*256)
            ax.set_ylim(-0.15, 1.8)
            f.canvas.draw()
        print("Plotted!")

    def plot(self):
        leds = self.aligner.led_coords
        fibre = self.aligner.fibre_coords
        ax = self.fig.gca()
        ax.clear()
        ax.imshow(self.image)
        ax.axis("off")
        if len(leds):
            vertx = [leds[0][0], leds[-1][0]]
            verty = [leds[0][1], leds[-1][1]]
            ax.plot(vertx, verty, c='r') # vertical
            if len(leds) == 4:
                ax.plot(*leds[1:3].T, c='r') # horizontal
        if len(fibre):
            ax.scatter(*fibre, c="r", s=35)
        self.fig.canvas.draw()

pages = [Page1]

GUI = gui.Root(pages)
GUI.mainloop()
