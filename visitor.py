import gui as G

class Page1(G.Page):
    def __init__(self, parent, controller):
        G.Page.__init__(self, parent, controller, langfile = "visitor1_lang", nextpage = Page2)
        self.title = G.tk.Label(self, text = "VISITOR PAGE 1", font = G.LABEL_FONT)
        self.title.grid(row = 0, column = 1, columnspan = 10, stick = "news")
        
        self.sun = G.Sun(parent = self, width = 600, height = 400, padx=25, pady=10, background="#000000")
        self.sun.grid(row = 1, column = 1)
        
class Page2(G.Page):
    def __init__(self, parent, controller):
        G.Page.__init__(self, parent, controller, langfile = "visitor2_lang", previous = Page1, nextpage = Page1)
        self.title = G.tk.Label(self, text = "VISITOR PAGE 2", font = G.LABEL_FONT)
        self.title.grid(row = 0, column = 1, columnspan = 10, stick = "news")
        
pages = [Page1, Page2]

GUI = G.Root(pages)
GUI.mainloop()
