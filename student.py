import gui as G

class Page1(G.Page):
    def __init__(self, parent, controller):
        G.Page.__init__(self, parent, controller, langfile = "student_lang")
        
        self.title = G.tk.Label(self, text = "STUDENT SCREEN", font = G.LABEL_FONT)
        self.title.grid(row = 0, column = 1, columnspan = 10, stick = "news")
        
        self.controls = G.Controls(parent = self, controller = self.controller)
        self.controls.grid(row = 1, column = 1, sticky = "n", padx = 25)
        
        self.spectrum = G.Spectrum(parent = self, controller = self.controller)
        self.spectrum.grid(row = 1, column = 2, sticky = "n", padx = 25)
        
        self.translatables = [self.title, self.controls.sun.button, self.controls.align.button, self.spectrum.button, self.spectrum.label_integration]
        
    def take_spectrum(self):
        filename = G.expose(self.e_exposure.get()) # expose image; returns filename where spectrum was saved
        data = G.reduce_spectrum(filename) # remove dark
        G.plot_spectrum(data, self.f_spectrum, self.a_exp, self.a_spec) # display images

pages = [Page1]

GUI = G.Root(pages)
GUI.mainloop()
