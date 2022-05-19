# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 20:53:45 2020

@author: UTILISATEUR
"""

import serial
import time
import matplotlib.pyplot as plt
import numpy as np
import sys
import datetime
from PyQt5 import QtWidgets, QtCore, QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pyqtgraph as pg
class MainWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Temperature SoftWare")
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)


        self.ser = serial.Serial('COM3', 9600, timeout=1)
        time.sleep(2)
        # self.temp = 0
        self.T =  [0,0.001]
        self.data = [25,25]
        self.started = 0
        self.t = 0
        self.nbTicks = 1
        self.hours = []
        self.Fan, self.Window, self.Game = False, False,False

        self.figure = Figure()
        self.figure.autofmt_xdate()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot()
        self.ax.yaxis.set_ticks(np.arange(15, 30, 1))

        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Temp °C')
        self.ax.yaxis.grid()

        self.line, = self.ax.plot(self.data, self.T, color = "b")
        self.line_dot, = self.ax.plot([], [], color = "r")
        self.canvas = FigureCanvas(self.figure)

        MainLayout =  QtWidgets.QHBoxLayout()

        CanvasLayout =  QtWidgets.QHBoxLayout()

        CanvasLayout.addWidget(self.canvas)


        ControlLayout =  QtWidgets.QVBoxLayout()
        PannelLayout = QtWidgets.QVBoxLayout()
        self.ControlBox = QtWidgets.QGroupBox("Control Pannel")
        self.ControlBox.setMinimumWidth(200)
        self.ControlBox.setMaximumWidth(200)

        self.AverageLabel = QtWidgets.QLabel("Average temp:")
        self.MaxLabel = QtWidgets.QLabel("Max temp:")
        self.MinLabel = QtWidgets.QLabel("Min temp:")

        self.FanButton = QtWidgets.QPushButton("Fan")
        self.WindowButton = QtWidgets.QPushButton("Window")
        self.GameButton = QtWidgets.QPushButton("Game")
        self.ControlBox.setLayout(PannelLayout)

        PannelLayout.addWidget(self.AverageLabel)
        PannelLayout.addWidget(self.MaxLabel)
        PannelLayout.addWidget(self.MinLabel)
        PannelLayout.addWidget(self.FanButton)
        PannelLayout.addWidget(self.WindowButton)
        PannelLayout.addWidget(self.GameButton)
        ControlLayout.addWidget(self.ControlBox)

        self.WindowButton.clicked.connect(self.WindowPressed)
        self.FanButton.clicked.connect(self.FanPressed)
        self.GameButton.clicked.connect(self.FanPressed)


        MainLayout.addLayout(ControlLayout)
        MainLayout.addLayout(CanvasLayout)




        self.setLayout(MainLayout)

        self.time0 = time.time()
        self.Drawtimer = pg.QtCore.QTimer()
        self.Drawtimer.timeout.connect(self.plot)
        self.Drawtimer.start(1) # refresh rate in ms

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.changeIcon)
        self.timer.start(2000) # refresh rate in ms

    def WindowPressed(self):
        self.Window = not self.Window
        if self.Window:
            color = "r"
        else:
            color = "r--"
        self.ax.plot([self.t for _ in range(16)],np.arange(15,31),color,linewidth=0.5)
    def FanPressed(self):
        self.Fan = not self.Fan
        if self.Fan:
            color = "g"
        else:
            color = "g--"
        self.ax.plot([self.t for _ in range(16)],np.arange(15,31),color,linewidth=0.5)
    def GamePressed(self):
        self.Game = not self.Game
        if self.Fan:
            color = "b"
        else:
            color = "b--"
        self.ax.plot([self.t for _ in range(16)],np.arange(15,31),color,linewidth=0.5)
    def controlPannel(self):
        average = np.mean(self.data)
        max_value = np.max(self.data)
        min_value = np.min(self.data)
        self.AverageLabel.setText(f"Average temp: {round(average,1)}°C")
        self.MaxLabel.setText(f"Max temp: {round(max_value,1)}°C")
        self.MinLabel.setText(f"Min temp: {round(min_value,1)}°C")

    def getTemp(self):
        t0 = time.perf_counter()
        b = self.ser.readline()         # read a byte string
        string_n = b.decode()  # decode byte string into Unicode
        string = string_n.rstrip() # remove \n and \r
        if string == "": return None
        temp = float(string)       # convert string to float
        if temp > 75: return None
        if temp < -15: return None
        tf = time.perf_counter()
        # print(round((tf - t0)*1000),"ms")
        return temp

    def plot(self):
        d = datetime.datetime.now()
        ds = time.time() - self.time0
        self.dstr = str(d)[11:16]
        self.nbTicks += 1
        if self.nbTicks % 30 != 0:
            self.hours.append("")
        else:
            self.hours.append(self.dstr)

        # print(self.hours)

        # self.ax.set_xticklabels(self.hours, fontsize = 8,rotation = 60)
        dt = 0.5
        t0 = time.perf_counter()
        self.temp = self.getTemp() #FUNCTION CALL

        if self.temp is None: return
        self.data.append(self.temp)

        if len(self.data) >50000:
            self.data = self.data[1:]
            self.T = self.T[1:]
        if len(self.data) == 4 and self.started < 2:
            self.data = self.data[1:]
            self.T = self.T[1:]
            self.started += 1
        self.t = ds
        self.T.append(ds)

        # y_dot = np.mean(self.data) + np.diff(self.data)/np.diff(self.T)*2
        self.line.set_data(self.T,self.data)
        #self.line_dot.set_data(self.T[:-1], y_dot)
        plt.pause(0.0001)
        #time.sleep(dt)

        self.canvas.draw()
        self.ax.set_xlim(min(self.T), max(self.T))
        self.ax.set_ylim(20,30)
        self.ax.set_xlabel(f'Time ({round(ds)})')


        if len(self.data) > 1000:
            average2 = np.mean(self.data[-500:])
            average1 = np.mean(self.data[-1000:-500])
            diff = (average2 - average1)*100
        else:
            diff = 0
        # dy = np.gradient(self.data) * 0.5

        # self.ax.plot(self.T, dy + 25, c="r")
        self.ax.set_title(f"Temp : {round(self.temp,1)}°C |{round(diff,1)} ")
        self.controlPannel()
        self.ax.xaxis.set_ticks(np.linspace(self.T[0], self.T[-1], 12))
        tf = time.perf_counter()
        print(self.temp,"°C -",round((tf - t0)*1000),"ms", round(diff,1))



    def changeIcon(self):
        import ctypes
        myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        temp = self.getTemp()
        if temp is None: return
        strtemp = str(round(temp))
        self.setWindowIcon(QtGui.QIcon(f"D:\JLP\_INFORMATIQUE_\_FILES_\PHOTOS\Temperatures\{strtemp}.jpg"))
        self.setWindowTitle(f"Temperature : {round(temp,1)}°C")



if __name__ == '__main__':
    import ctypes
    myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QtWidgets.QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())