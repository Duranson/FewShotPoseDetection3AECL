from __future__ import division
from tkinter import *
from PIL import Image, ImageTk
import tkinter.ttk as ttk
import os
import glob
import random
import config
from math import pi, cos, sin
import numpy as np

# colors for the bboxes
COLORS = ['red', 'blue', 'olive', 'teal', 'cyan', 'green', 'black']
# image sizes for the examples
SIZE = 256, 256


class AnnotationTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("AnnotationTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)

        self.parent.resizable(width=FALSE, height=FALSE)

		# initialize global state
        self.imageName = ''
        self.outName = ''
        self.imageFormat = config.PARAMS['imageFormat']
        self.sourceImageDir = config.PARAMS['sourceImageDirectory']
        self.annotationDir = config.PARAMS['annotationDirectory']
        
        self.azimuth = 0
        self.elevation = 0
        self.zRotation = 0
        

		# ----------------- GUI stuff ---------------------
		# dir entry & load
        self.label = Label(self.frame, text="Image Path:")
        self.label.grid(row=0, column=0, sticky=E)
        self.entry = Entry(self.frame)
        self.entry.grid(row=0, column=1, sticky=W + E)
        self.ldBtn = Button(self.frame, text="Load", command=self.loadImage)
        self.ldBtn.grid(row=0, column=2, sticky=W + E)

		# main panel for labeling
        self.mainPanel = Canvas(self.frame)
        self.mainPanel.grid(row=1, column=1, rowspan=4, sticky=W + N)
        
        self.mainPanel.bind('<Up>',self.upRotation)
        self.mainPanel.bind('<Down>',self.downRotation)
        self.mainPanel.bind('<Right>',self.rightRotation)
        self.mainPanel.bind('<Left>',self.leftRotation)
        self.mainPanel.bind('<w>',self.trigoRotation)
        self.mainPanel.bind('<x>',self.antitrigoRotation)

		# showing bbox info & delete bbox
        self.infoCanvas = Frame(self.frame)
        self.infoCanvas.grid(row = 1, column = 2)
        self.lb2 = Label(self.infoCanvas, text='Euler Angles:')
        self.lb2.grid(row=1, column=1,  sticky=W + N)
        self.azimuthText = StringVar()
        self.elevationText = StringVar()
        self.zRotationText = StringVar()
        self.azimuthLabel = Label(self.infoCanvas, width=22, height=12, textvariable = self.azimuthText)
        self.azimuthLabel.grid(row=2, column=1, sticky=N + S)
        self.elevationLabel = Label(self.infoCanvas, width=22, height=12, textvariable = self.elevationText)
        self.elevationLabel.grid(row=3, column=1, sticky=N + S)
        self.zRotationLabel = Label(self.infoCanvas, width=22, height=12, textvariable = self.zRotationText)
        self.zRotationLabel.grid(row=4, column=1, sticky=N + S)
        
        self.azimuthText.set("Azimuth = 0")
        self.elevationText.set("Elevation = 0")
        self.zRotationText.set("zRotation = 0")
		# control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row=7, column=1, columnspan=2, sticky=W + E)
        self.nextBtn = Button(self.ctrPanel, text='Save',
							  width=10, command=self.saveImage)
        self.nextBtn.pack(side=LEFT, padx=5, pady=3)

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(4, weight=1)

    def loadImage(self):
        self.imageName = "./Images/" + self.entry.get()
        # output txt file
        self.outName = self.imageName + '-annotations.txt'
        # load image
        self.img = Image.open(self.imageName)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width=max(self.tkimg.width(), 400),
							  height=max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image=self.tkimg, anchor=NW)
        self.mainPanel.focus_set()

    def saveImage(self):
        if self.outName:
            with open(self.outName, 'w') as f:
                f.write(f"{self.azimuth} {self.elevation} {self.zRotation}")
                print(f'Image No. saved at {self.outName}')

    def traceCoordinateSystem(self):
        self.mainPanel.delete('all')
        self.mainPanel.create_image(0, 0, image=self.tkimg, anchor=NW)
        print(self.azimuth, self.elevation, self.zRotation)
        # Azimuth is between [0, 360), Elevation is between (-90, 90), In-plane Rotation is between [-180, 180)
        azi = self.azimuth / 180 * pi * (-1)
        ele = self.elevation / 180 * pi
        rot = self.zRotation / 180 * pi * (-1)
        
        start_point = (self.img.size[0] // 2, self.img.size[1] // 2)
        
        rotation_matrix = np.array([
            [ cos(azi)*cos(rot) , -cos(azi)*sin(rot) , sin(azi) ],
            [ cos(ele)*sin(rot) + sin(ele)*sin(azi)*cos(rot),  cos(ele)*cos(rot) - sin(ele)*sin(azi)*sin(rot), -sin(ele) * cos(azi) ],
            [ sin(ele)*sin(rot) - cos(ele)*sin(azi)*cos(rot),  sin(ele)*cos(rot) + cos(ele)*sin(azi)*sin(rot), cos(ele) * cos(azi) ]
            ])
    
        bar_size = 300
        X = rotation_matrix.dot(np.array([[bar_size,0,0]]).T)
        Y = rotation_matrix.dot(np.array([[0,bar_size,0]]).T)
        Z = rotation_matrix.dot(np.array([[0,0,bar_size]]).T)
    
        # projections to the screen
        Xp = np.array(X[0:2].T[0])
        Yp = np.array(Y[0:2].T[0])
        Zp = np.array(Z[0:2].T[0])
        Xp_shape = [start_point ,(start_point[0] - int(Xp[0]),start_point[1] - int(Xp[1]))]
        Yp_shape = [start_point ,(start_point[0] - int(Yp[0]),start_point[1] - int(Yp[1]))]
        Zp_shape = [start_point ,(start_point[0] - int(Zp[0]),start_point[1] - int(Zp[1]))]
        
        self.mainPanel.create_line(Xp_shape[0][0], Xp_shape[0][1], Xp_shape[1][0], Xp_shape[1][1],fill = "red", width = 3)
        self.mainPanel.create_line(Yp_shape[0][0], Yp_shape[0][1], Yp_shape[1][0], Yp_shape[1][1],fill = "green", width = 3)
        self.mainPanel.create_line(Zp_shape[0][0], Zp_shape[0][1], Zp_shape[1][0], Zp_shape[1][1],fill = "blue", width = 3)
        
        self.azimuthText.set(f"Azimuth : {self.azimuth}")
        self.elevationText.set(f"Elevation : {self.elevation}")
        self.zRotationText.set(f"zRotation : {self.zRotation}")
    
    def upRotation(self,event):
        self.elevation += 1
        self.traceCoordinateSystem()
    
    def downRotation(self,event):
        self.elevation -= 1
        self.traceCoordinateSystem()
    
    def rightRotation(self,event):
        self.azimuth += 1
        self.traceCoordinateSystem()
        
    def leftRotation(self,event):
        self.azimuth -= 1
        self.traceCoordinateSystem()
    
    def trigoRotation(self,event):
        self.zRotation += 1
        self.traceCoordinateSystem()
    
    def antitrigoRotation(self,event):
        self.zRotation -= 1
        self.traceCoordinateSystem()
    

if __name__ == '__main__':
	root = Tk()
	tool = AnnotationTool(root)
	root.resizable(width=True, height=True)
	root.mainloop()
