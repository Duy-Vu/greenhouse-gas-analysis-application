# Imports
import matplotlib  # type: ignore
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as Canvas  # type: ignore
from matplotlib.figure import Figure  # type: ignore
from PyQt6 import QtWidgets

# Ensure using PyQt6 backend
matplotlib.use("QTAgg")


# Matplotlib canvas class to create figure
class MplCanvas(Canvas):
    fig: Figure
    ax: matplotlib.axes.Axes

    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        Canvas.__init__(self, self.fig)
        Canvas.updateGeometry(self)


# Matplotlib widget
class MplWidget(QtWidgets.QWidget):
    canvas: MplCanvas
    vbl: QtWidgets.QVBoxLayout

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)  # Inherit from QWidget
        self.canvas = MplCanvas()  # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()  # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
