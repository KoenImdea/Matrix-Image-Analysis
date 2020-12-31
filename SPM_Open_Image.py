"""
v0.2 Started on 24/08/2018

Author: Koen

Purpose: Convert photonmaps using Python to WsXM readable format.
Important: Code must be re-uable for advanced data-analysis later.

"""
#Import tkinter for GUI
import tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from tkinter import filedialog
#We'll mare use of numpy
import numpy as np
#Just in case we want tu use a special character
import re

#Import os to help with filename stuff
import os
#Import stuff needed for Matplotlib
import matplotlib as mpl
#import my SMP analysis library
import SPM_Analysis as sa

#To do image analysis
import spiepy
#To plot

from scipy.ndimage import gaussian_filter
import math



flat_options = ["None", "Linewise Mean", "Linewise Polynomal", "flatten_by_iterate_mask", "flatten_by_peaks", "flatten_xy", "flatten_poly_xy"]



"""Create GUI"""
class Mainwindow:
    def __init__(self, master):

        self.master = master

        #Create main menu
        menu = tkinter.Menu(master)
        master.config(menu=menu)
        #Create File menu, which contains load etc
        Filemenu = tkinter.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=Filemenu)
        Filemenu.add_command(label="Load Matrix Session", command=self.loadsession)
        Filemenu.add_command(label="Export Image", command=self.export_image)
        #Filemenu.add_command(label="Export Intensitymap", command=self.export_intensitymap)
        Filemenu.add_command(label="Exit", command = root.quit)
        #Create edit menu for fittings
        Editmenu = tkinter.Menu(menu, tearoff=0)
        menu.add_cascade(label="Edit", menu=Editmenu)
        Editmenu.add_command(label="Show STS", command=self.show_STS)

        # Create a container to add the data navigation input spinboxes
        navigation = tkinter.Frame(master)
        #Make a list to display image_filenames
        self.listbox = tkinter.Listbox(navigation)
        self.listbox.pack(side="left", fill=tkinter.Y)
        self.listbox.bind("<<ListboxSelect>>", self.showimg)




        # Create a container to add the data smoothing input spinboxes
        flattening = tkinter.Frame(master)
        # Create 2 labels and spinboxes
        self.label_option = tkinter.Label(flattening, text="Flatten Option:")
        self.label_option.pack(side="left")
        self.flat_method = tkinter.StringVar(flattening)
        self.flat_method.set(root.flat_options[1]) # default value

        self.option_method = tkinter.OptionMenu(flattening, self.flat_method, *root.flat_options)
        self.option_method.pack(side="left")


        self.label_order = tkinter.Label(flattening, text="Order for Poly:")
        self.label_order.pack(side="left")
        self.spinbox_order = tkinter.Spinbox(flattening, from_=0, to=12, increment = 1)
        self.spinbox_order.pack(side="left")

        self.label_smooth = tkinter.Label(flattening, text="Smoothing:")
        self.label_smooth.pack(side="left")
        self.spinbox_smooth = tkinter.Spinbox(flattening, from_=0, to = 5)
        self.spinbox_smooth.pack(side="left")

        #Define empty x and y data for the graph
        x = 0 #Map[int(self.spinbox_x_min.get()):int(self.spinbox_x_max.get()),0]
        y = 0 #Map[int(self.spinbox_x_min.get()):int(self.spinbox_x_max.get()),int(self.spinbox_curve_nr.get())]

        #Start drawing the figure
        self.palette = spiepy.NANOMAP
        self.palette.set_bad('r', 1.0)

        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig,master=master)
        self.canvas.draw()

        navigation.pack(side="left", fill=tkinter.Y)
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

        #pack the previously defined frame under the figure

        flattening.pack()

    def showimg(self, trash):
        """Here, if we need we update the topography image"""

        #First check if the listbox has a valid selection
        if not(self.listbox.curselection() == ()):
            #If we are going to update we need to clear the axes.
            self.ax.clear()
            #Is spectroscopy is being shown, we want to close it
            if root.sts_window == True:
                self.close_sts_window()

            #get the new intex from the listboz
            self.index = self.listbox.curselection()

            #The index corresponds 1:1 with the root filechain index
            self.image = sa.open_image(root.filechain[self.index[0]])

            #We always show the last part to be user friendly
            self.last_part = root.filechain[self.index[0]][root.filechain[self.index[0]].rindex('--') + 2:]

            #Also, get the run number to check it there is spectroscopy in this run_cycle
            #This way we can show spectra in all channels (I, Z, aux,...)
            self.run_number = self.last_part[0:self.last_part.find(".")]

            #Find out if there has been spectroscopy in this run:
            self.found = False
            self.key = ""
            for key in root.sts_dict.keys():
                last_part = key[key.rindex('--') + 2:]
                run_number = last_part[0:last_part.find(".")]
                if run_number == self.run_number:
                    self.found = True
                    self.key = key



            #Do the required flattening
            if self.flat_method.get() == root.flat_options[1]:
                self.flattened = sa.line_filtered(self.image.data)
            elif self.flat_method.get() == root.flat_options[2]:
                self.flattened = sa.poly_line_filtered(self.image.data, int(self.spinbox_order.get()))
            elif self.flat_method.get() == root.flat_options[3]:
                self.flattened = sa.flatten_by_iterate_mask(self.image.data)
            elif self.flat_method.get() == root.flat_options[4]:
                self.flattened = sa.flatten_by_peaks(self.image.data)
            elif self.flat_method.get() == root.flat_options[5]:
                self.flattened = sa.flatten_xy(self.image.data)
            elif self.flat_method.get() == root.flat_options[6]:
                self.flattened = sa.flatten_poly_xy(self.image.data, int(self.spinbox_order.get()))
            else:
                self.flattened = self.image.data

            #Do required smoothing
            if not(int(self.spinbox_smooth.get()) == 0):
                self.flattened = gaussian_filter(self.flattened[:,:], sigma=[int(self.spinbox_smooth.get()),int(self.spinbox_smooth.get())])

            #plot the flattened and smoothened image
            self.ax.imshow(self.flattened, cmap = self.palette, origin = 'lower', extent=[-(self.image.XY_width * 1E9)/2, (self.image.XY_width * 1E9)/2, -(self.image.XY_height * 1E9)/2, (-(self.image.XY_height * 1E9)/2) + self.image.height *1E9] )
            #add the name of the image
            self.ax.set_xlabel(self.last_part, color='black')
            #add voltage and current in the title
            self.title = ("Vt = " + str(round(self.image.voltage, 3)) +
                "V, It = " + str(round(self.image.current * 1E9, 3)) + "nA")

            self.dist_per_point = (self.image.XY_width / self.image.XY_points) * 1E9
            self.dist_per_line = (self.image.XY_height / self.image.XY_lines) * 1E9

            #If spectra, but trouble assigning them:say so
            if self.key in root.bad_keys:
                self.title = self.title + "\n" + "Image has spectra, but we are unable to assign them unambiguously."
            #If spectra, and no trouble assigning them: do so
            elif self.found:
                self.title = self.title + "\n" + "Number of spectra = " + str(len(root.sts_dict[self.key][1]))
                for h in range(0, len(root.sts_dict[self.key][1])):
                    self.ax.plot((root.sts_dict[self.key][1][h][0] - self.image.XY_points/2) * self.dist_per_point, (root.sts_dict[self.key][1][h][1] - self.image.XY_points/2) * self.dist_per_point,
                            'o', mfc = '#ffffff', ms = 5)

            #Set title for graph
            self.ax.set_title(self.title)
            #rescale
            self.ax.relim()
            self.ax.autoscale_view()
            #draw
            self.canvas.draw()



    #What to do upon x_min change, i.e. redraw graph
    def x_min(self):
        global Map
        x = 0 #Map[int(self.spinbox_x_min.get()):int(self.spinbox_x_max.get()),0]
        y = 0 #Map[int(self.spinbox_x_min.get()):int(self.spinbox_x_max.get()),int(self.spinbox_curve_nr.get())]
        self.line1.set_data(x,y)
        self.line2.set_data(x,y)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    #What to do upon x_max change, i.e. redraw graph
    def x_max(self):
        global Map
        x = 0 #Map[int(self.spinbox_x_min.get()):int(self.spinbox_x_max.get()),0]
        y = 0 #Map[int(self.spinbox_x_min.get()):int(self.spinbox_x_max.get()),int(self.spinbox_curve_nr.get())]
        self.line1.set_data(x,y)
        self.line2.set_data(x,y)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    #What to do upon curve_nr change, i.e. redraw graph
    def curve_nr(self):
        global Map
        x = 0 #Map[int(self.spinbox_x_min.get()):int(self.spinbox_x_max.get()),0]
        y = 0 #Map[int(self.spinbox_x_min.get()):int(self.spinbox_x_max.get()),int(self.spinbox_curve_nr.get())]
        self.line1.set_data(x,y)
        self.line2.set_data(x,y)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()


    def show_STS(self):
        """Open Second Window to show the STS curves"""
        if root.sts_window == False:
            self.sts_window = tkinter.Toplevel(self.master)
            self.sts_window.title('Second window')
            self.janela_remessas = STSWindow(self.sts_window)
            root.sts_window = True
            self.sts_window.wm_protocol("WM_DELETE_WINDOW", lambda: self.close_sts_window())

    def close_sts_window(self, *event):
        """If we close the window, we should signal main app """
        #rint("closing window")
        root.update_idletasks()
        root.sts_window = False
        self.sts_window.destroy()

    def loadsession(self):
        """Define loading omicron filechain"""
        #Step one: get filename & reset variables
        root.map_path = filedialog.askopenfilename(filetypes=(("Matrix Session", "*.mtrx"),("All files", "*.*")))

        root.filechain = []
        root.sts_dict = {}
        root.sts_numbers_dict = {}
        root.bad_keys = []
        root.to_remove = []
        self.listbox.delete(0, tkinter.END)

        #Step 2: Use handy routine from SPM_Analysis to load the file
        root.filechain, root.sts_dict = sa.load_filechain(root.map_path)

        #Create the STS numbers dicht to truly get the number of spectra
        #This is to not cound I(V) and aux(v), or repeaded spectra double
        sts_numbers = []
        for key in root.sts_dict.keys():
            for i in root.sts_dict[key][0]:
                last_part = i[i.rindex('--') + 2:]
                if not last_part[0:last_part[0:last_part.find(".")].find("_")] in sts_numbers:
                    sts_numbers.append(last_part[0:last_part[0:last_part.find(".")].find("_")])
            root.sts_numbers_dict[key] = sts_numbers
            sts_numbers = []

        #Now check is spectra numbers == # of sts_location
        #If not, we cannot assign location reliably -> in bad_key dict
        root.bad_keys = []
        for key in root.sts_dict.keys():
            if not(len(root.sts_dict[key][1]) == len(root.sts_numbers_dict[key])):
                root.bad_keys.append(key)

        #Step 4: Update list for file selection
        for file in root.filechain:
               self.listbox.insert(tkinter.END, file[file.rindex('--') + 2:])
        #print(root.sts_dict)
        #print(root.filechain)
        #print(root.sts_numbers_dict)


    def export_image(self):
        """Define exporting matplotlib figure"""

        #Step one: Determine filename
        root.save_path = filedialog.asksaveasfilename(filetypes=(("png","*.png"), ("pdf","*.pdf")))

        #Step two: Use handy function to save image
        self.fig.savefig(root.save_path)



class STSWindow:
    def __init__(self,master,*args,**kwargs):
        #super().__init__(master,*args,**kwargs)
        #COpen STS window
        # Create a container to add the data navigation input spinboxes
        navigationSTS = tkinter.Frame(master)
        #Make a list to display image_filenames
        self.listboxSTS = tkinter.Listbox(navigationSTS)
        self.listboxSTS.pack(side="left", fill=tkinter.Y)
        self.listboxSTS.bind("<<ListboxSelect>>", self.showSTS)

        # Create a container to add the data smoothing input spinboxes
        smoothing = tkinter.Frame(master)
        # Create 2 labels and spinboxes


        self.label_smooth = tkinter.Label(smoothing, text="Smoothing:")
        self.label_smooth.pack(side="left")
        self.spinbox_smooth = tkinter.Spinbox(smoothing, from_=0, to = 5)
        self.spinbox_smooth.pack(side="left")

        #Define empty x and y data for the graph
        x = 0 #Map[int(self.spinbox_x_min.get()):int(self.spinbox_x_max.get()),0]
        y = 0 #Map[int(self.spinbox_x_min.get()):int(self.spinbox_x_max.get()),int(self.spinbox_curve_nr.get())]

        #Start drawing the figure


        navigationSTS.pack(side="left", fill=tkinter.Y)


        self.figSTS = Figure()
        self.axSTS = self.figSTS.add_subplot(111)

        self.canvasSTS = FigureCanvasTkAgg(self.figSTS,master=master)
        self.canvasSTS.draw()

        self.canvasSTS.get_tk_widget().pack(side='top', fill='both', expand=1)

        #pack the previously defined frame under the figure

        smoothing.pack()
        #fill the listbox with the relevant spectra
        if (app.key in root.sts_dict.keys()) and not (app.key in root.bad_keys):

            for value in root.sts_dict[app.key][0]:
                self.listboxSTS.insert(tkinter.END, value[value.rindex('--') + 2:])



    def close_window(self, *event): #Please fix me!
        root.STS_window = False

        self.destroy()

    def showSTS(self, trash):
        if not(self.listboxSTS.curselection() == ()):
            if self.listboxSTS.size() > 0:




                app.ax.clear()

                app.ax.imshow(app.flattened, cmap = app.palette, origin = 'lower', extent=[-(app.image.XY_width * 1E9)/2, (app.image.XY_width * 1E9)/2, -(app.image.XY_height * 1E9)/2, (-(app.image.XY_height * 1E9)/2) + app.image.height *1E9] )
                app.ax.set_xlabel(app.last_part, color='black')

                app.ax.set_title(app.title)
                app.ax.relim()
                app.ax.autoscale_view()


                self.axSTS.clear()

                index = self.listboxSTS.curselection()[0]
                number = self.listboxSTS.get(index)
                number = number[0:number[0:number.find(".")].find("_")]
                filename = root.sts_dict[app.key][0][index]
                #print(root.filechain[app.index[0]])


                self.curve = sa.open_curve(filename)

                self.axSTS.plot(self.curve.data[0][:], self.curve.data[1][:])
                self.axSTS.set_xlabel(self.curve.x_data_name_and_unit)
                self.axSTS.set_ylabel(self.curve.y_data_name_and_unit)

                coordinate_index = root.sts_numbers_dict[app.key].index(number)

                coordinates = root.sts_dict[app.key][1][coordinate_index]

                app.ax.set_xlabel(app.last_part + " Point at: " + str((coordinates[0],coordinates[1])), color='black')



                app.ax.plot((coordinates[0] - app.image.XY_points/2) * app.dist_per_point, (coordinates[1] - app.image.XY_lines/2)* app.dist_per_line,
                            'o', mfc = '#ffffff', ms = 5)

                app.canvas.draw()

                self.canvasSTS.draw()




"""Create tkinter instance and use it to launch our class. Then put it in loop to maintain it alive and wait for user input"""
root = tkinter.Tk()
"""Define variables so that they are global"""
#The matrix session that we will be opening
root.map_path = ""
#Here all filenames of its filechain will be stored
root.filechain = []

#We will make a dictionary of: {image_filenames: [spectra_filenames, locations]}
root.sts_dict = {}
#The problem with the filenames dict is that there can be various filenames for one location.
#I have to make a second dict with only the numbers to check #spectra against #location
root.sts_numbers_dict = {}
#If #spectra is not equeal to #location, image_filename is placed in bad_keys.
#We use this to warn the users that a file contains spectra, but we cannot assign locations
root.bad_keys = []
#This is for if we expect that a topo image is bad
root.to_remove = []
#Here we are going to store all the [last_part, mtrx_data]
root.image_chain = []
root.flat_options = ["None", "Linewise Mean", "Linewise Polynomal", "flatten_by_iterate_mask", "flatten_by_peaks", "flatten_xy", "flatten_poly_xy"]

root.sts_window = False


app = Mainwindow(root)
root.mainloop()
