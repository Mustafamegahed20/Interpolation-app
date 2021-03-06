from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QFileDialog, QMessageBox
import sys
from PyQt5.uic.properties import QtCore
from PyQt5.QtCore import pyqtSignal
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import os
import pandas as pd
import more_itertools as mit
import mplwidget

from sklearn.metrics import mean_absolute_error
from sympy import S, symbols, printing
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('Gui.ui', self)
        self.setWindowTitle("Interpolation application")
        self.upload.clicked.connect(self.open)

        self.display.clicked.connect(self.chunk)
        self.slider1.valueChanged.connect(self.chunk)
        self.slider2.valueChanged.connect(self.chunk)
        self.spinBox1.valueChanged.connect(self.chunk)
        self.spinBox2.valueChanged.connect(self.chunk)

        self.errorMap.clicked.connect(self.error_map)

        self.comboBox.currentIndexChanged.connect(self.changeTitle)

        self.MplWidget.canvas.axes.set_facecolor('black')
        self.MplWidget2.canvas.axes.set_facecolor('black')
        self.show()

    def open(self):
        global data0
        path = QFileDialog.getOpenFileName(self, 'Open a file', '', 'Choose arbitrary signal(*.csv)')
        if path != ('', ''):
            data0 = path[0]
            # logging.info("The user open an audio file path: " + data)
            print(data0)

    def chunk(self):
        global data0
        global chunks, degree, x, y, model, x_chunks, y_chunks

        data = pd.read_csv(data0)
        x_data = data['# t']
        y_data = data['x']
        chunks = int(self.spinBox1.value())
        degree = self.slider1.value()

        if (chunks == 1):
            self.comboBox.clear()
            self.slider2.setEnabled(True)
            change = round(self.slider2.value() / 100 * len(x_data))  # changing %
            x = x_data[:change]  # change from last value towards beginning of array
            y = y_data[:change]  # change from last value towards beginning of array

            modelExtrapolation = np.poly1d(np.polyfit(x, y, degree))
            self.MplWidget.canvas.axes.clear()
            self.MplWidget.canvas.axes.plot(x_data, y_data, '--')
            self.MplWidget.canvas.axes.plot(x_data, modelExtrapolation(x_data), '-.')

            p = np.polyfit(x, y, degree)
            xSymbols = symbols("x")
            poly = sum(S("{:6.2f}".format(v)) * xSymbols ** i for i, v in enumerate(p[::1]))
            eq_latex = printing.latex(poly)
            label = "${}$".format(eq_latex)
            # print(label)
            self.MplWidget.canvas.axes.set_title(label, color='b', fontsize=15)
            self.MplWidget.canvas.draw()

        else:
            self.slider2.setValue(100)
            self.slider2.setEnabled(False)
            change = round(100 / 100 * len(x_data))  # changing %
            x = x_data[:change]  # change from last value towards beginning of array
            y = y_data[:change]  # change from last value towards beginning of array

            n = int((len(x) - 1) / chunks)
            percentage = int(self.spinBox2.value())
            if (percentage >= 0 and percentage <= 25):
                k = int((percentage / 100) * ((len(x) - 1) / chunks))
                x_chunks = list(mit.windowed(x, n=int(len(x) / chunks), step=n - k))
                y_chunks = list(mit.windowed(y, n=int(len(x) / chunks), step=n - k))
                self.MplWidget.canvas.axes.clear()

            self.MplWidget.canvas.axes.plot(x_data, y_data, '--')
            # labels = []
            self.comboBox.clear()

            for i in range(chunks):
                self.MplWidget.canvas.axes.tick_params(axis="x", colors="white")
                self.MplWidget.canvas.axes.tick_params(axis="y", colors="white")
                # self.MplWidget.canvas.axes.plot(x_chunks[i], y_chunks[i],'--')

                model = np.poly1d(np.polyfit(x_chunks[i], y_chunks[i], degree))
                self.MplWidget.canvas.axes.plot(x_chunks[i], model(x_chunks[i]), '-.')

                p = np.polyfit(x_chunks[i], y_chunks[i], degree)
                xSymbols = symbols("x")
                poly = sum(S("{:6.2f}".format(v)) * xSymbols ** i for i, v in enumerate(p[::1]))
                eq_latex = printing.latex(poly)

                label = "${}$".format(eq_latex)

                self.comboBox.addItem(label)

                # self.MplWidget.canvas.axes.set_title(labels, color='b', fontsize=15)
                self.MplWidget.canvas.draw()

        self.MplWidget.canvas.draw()

    def changeTitle(self):
        self.MplWidget.canvas.axes.set_title(self.comboBox.currentText(), color='b', fontsize=15)
        self.MplWidget.canvas.draw()

    ######################################### Error Map ##################################
    def error_map(self):
        global chunks, degree, x, y, model, x_chunks, y_chunks

        a = range(1, chunks + 1)
        b = range(1, degree + 1)
        xa, xb = np.meshgrid(a, b, sparse=True)

        model2 = np.poly1d(np.polyfit(x, y, degree))
        Overall_Error = mean_absolute_error(y, model2(x))
        errors = []
        for i in range(1, degree + 1):
            degrees = np.poly1d(np.polyfit(x, y, i))
            for j in range(chunks):
                errors.append(mean_absolute_error(y_chunks[j], degrees(x_chunks[j])))
        print(errors)
        errors_2d = np.reshape(errors, (degree, chunks))
        print(errors_2d)

        self.MplWidget2.canvas.axes.clear()
        self.MplWidget2.canvas.axes.tick_params(axis="x", colors="white")
        self.MplWidget2.canvas.axes.tick_params(axis="y", colors="white")
        self.MplWidget2.canvas.axes.set_title("Percentage Error = " + str(Overall_Error * 100) + ' %', color='r',
                                              fontsize=15)

        cax = make_axes_locatable(self.MplWidget2.canvas.axes).append_axes("right", size="5%", pad="4%")
        cax.tick_params(axis="x", colors="white")
        cax.tick_params(axis="y", colors="white")

        cf = self.MplWidget2.canvas.axes.contourf(a, b, errors_2d)
        self.MplWidget2.canvas.axes.figure.colorbar(cf, cax=cax)
        self.MplWidget2.canvas.draw()

        self.progressBar.setValue(100)
        QMessageBox.information(self, "Error Map Completed", "The Error Map has been generated Successfully ")
        self.progressBar.setValue(0)
        cax.remove()


app = 0
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
app.exec_()
