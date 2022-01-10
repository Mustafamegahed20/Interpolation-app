# ------------------------------------------------------
# -------------------- mplwidget.py --------------------
# ------------------------------------------------------
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvas

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class MplWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        self.navi_toolbar = NavigationToolbar(self.canvas, self)  # create a navigation toolbar for our plot canvas

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        vertical_layout.addWidget(self.navi_toolbar)
        self.canvas.figure.set_facecolor("#302F2F")
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.figure.subplots_adjust(top=0.915, bottom=0.070, left=0.065, right=0.930, hspace=0.2, wspace=0.2)
        self.setLayout(vertical_layout)
