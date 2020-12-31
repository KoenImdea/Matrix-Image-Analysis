import access2thematrix_test
import SPM_Analysis
import spiepy, spiepy.demo
import os, re
import tkinter

def display_images(result_file_chain, root):
    filenames = os.listdir(folder)
    columns = 6
    image_count = 0
    window = Toplevel(root)
    window.wm_geometry("1300x900")
    canvas = Canvas(window, width = 1200, height = 800)
    canvas.grid(row=0, column=0, sticky= "news")
    #canvas.place(x=0, y=0)

    vsb = Scrollbar(window, orient="vertical", command=canvas.yview)
    vsb.grid(row=0, column=0, sticky="ns")
    canvas.configure(yscrollcommand= vsb.set)

    frame_image = Frame(canvas)
    frame_image.pack(expand=True, fill="both")
    #frame_image.grid_rowconfigure(0, weight = 1)
    #frame_image.grid_columnconfigure(0, weight = 1)
    canvas.create_window((0,0), window=frame_image, anchor="nw")


    ResultFiles = access2thematrix_test.ResultFilechain()
    data_containers, message = ResultFiles.open(result_file_chain)
    topo_images = []
    sts_curves = []
    for data_container in data_containers:

        if "(" in data_container:
            sts_curves.append(data_container)
        else:
            topo_images.append(data_container)


    path = os.path.dirname(data_file) + "\\"

    for name in topo_images:
        image_count += 1
        r, c = divmod(image_count - 1, columns)
        im = spm.openimage(path + name)
        im = Image.open(os.path.join(folder, name))
        resized = im.resize((200,200), Image.ANTIALIAS)
        tkimage = ImageTk.PhotoImage(resized)
        myvar = Label(frame_image, image = tkimage)
        myvar.image = tkimage
        myvar.grid(row=r, column = c)
        #print "here"

    window.mainloop()
