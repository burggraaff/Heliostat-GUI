from __future__ import print_function
import gui
from gui import tk, LABEL_FONT
from gui.fibre import Aligner, serial_no_1, serial_no_2
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
        """
        self.parent = parent
        self.controller = controller
        tk.Frame.__init__(self, self.parent, *args, **kwargs)
        self.x = self.y = -9999.9999
        self.fx = self.fy = -1

        self.aligner = Aligner()

        self.b_plot = tk.Button(self, text = "PHOTO", font = LABEL_FONT, height = 2, width = 10, command = self.photo)
        self.b_plot.grid(row = 0, column = 2, sticky = "news")
        self.b_find = tk.Button(self, text = "FIND LEDS", font = LABEL_FONT, height = 2, width = 10, command = self.find_leds)
        self.b_find.grid(row = 1, column = 2, sticky = "news")
        self.b_opti = tk.Button(self, text = "OPTIMISE", font = LABEL_FONT, height = 2, width = 10, command = self.optimise)
        self.b_opti.grid(row = 2, column = 2, sticky = "news")
        self.b_save = tk.Button(self, text = "SAVE", font = LABEL_FONT, height = 2, width = 10, command = self.save)
        self.b_save.grid(row = 3, column = 2, sticky = "news")

        self.fig = plt.figure(figsize=(10,10), facecolor = "none")
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=100)

        self.f = "{0}: {1:+.4f}" # format to print values in
        self.indicator_x = tk.Label(self, text = self.f.format("X", self.x), font = LABEL_FONT)
        self.indicator_x.grid(row = 0, column = 1, sticky = "w")
        self.indicator_y = tk.Label(self, text = self.f.format("Y", self.y), font = LABEL_FONT)
        self.indicator_y.grid(row = 1, column = 1, sticky = "w")
        self.indicator_f = tk.Label(self, text = "F: (-1, -1)", font = LABEL_FONT)
        self.indicator_f.grid(row = 2, column = 1, sticky = "w")

        self.update(periodic = True)

    def end(self):
        if self.aligner is not None:
            self.aligner.end()

    def update(self, periodic = False):
        self.x, self.y = self.aligner.get_current_positions()
        self.fx, self.fy = self.aligner.get_fibre_position()
        self.indicator_x["text"] = self.f.format("X", self.x)
        self.indicator_y["text"] = self.f.format("Y", self.y)
        self.indicator_f["text"] = "F: ({0:.0f}, {1:.0f})".format(self.fx, self.fy)
        if periodic:
            self.controller.after(1000, lambda: self.update(periodic = True))

    def photo(self):
        self.image = self.aligner.camera.led_image()
        self.plot()

    def find_leds(self):
        self.aligner.find_LEDs(self.image)
        self.update()
        self.plot()

    def optimise(self):
        pass

    def save(self):
        self.update()
        table = np.loadtxt("static/fibre_positions.txt")
        new_row = np.array([self.fx, self.fy, self.x, self.y])
        table = np.vstack((table, new_row))
        np.savetxt("static/fibre_positions.txt", table, fmt="%.4f")
        print("Saved!")

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
