from tkinter import *


class Application(Frame):
    def __init__(self, master):
        """ Initialize frame"""
        super(Application, self).__init__(master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        """Create 3 useless buttons"""
        #first one
        self.bttn1=Button(self, text ="I do nothing!")
        self.bttn1.grid()
        #second button
        self.bttn2 = Button(self)
        self.bttn2.grid()
        self.bttn2.configure(text ="Me too!")
        #third one
        self.bttn3 = Button(self)
        self.bttn3.grid()
        self.bttn3["text"]="And me also!"

root=Tk()
#alter window
root.title("The simpliest gui")
root.geometry("800x600")
app=Application(root)
root.mainloop()