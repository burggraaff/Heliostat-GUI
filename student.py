import gui

class Page1(gui.Page):
    def __init__(self, parent, controller):
        gui.Page.__init__(self, parent, controller, langfile = "student_lang")
        
        self.title = gui.tk.Label(self, text = "STUDENT SCREEN", font = gui.LABEL_FONT)
        self.title.grid(row = 0, column = 1, columnspan = 10, stick = "news")
        
        self.controls = gui.Controls(parent = self, controller = self.controller)
        self.controls.grid(row = 1, column = 1, sticky = "n", padx = 25)
        
        self.spectrum = gui.Spectrum(parent = self, controller = self.controller)
        self.spectrum.grid(row = 1, column = 2, sticky = "n", padx = 25)
        
        self.translatables = [self.title, self.controls.sun.button, self.controls.align.button, self.spectrum.button, self.spectrum.label_integration]

pages = [Page1]

GUI = gui.Root(pages)
GUI.mainloop()
