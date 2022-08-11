import sys
import numpy as np

from PyQt5.QtWidgets import QApplication
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg


class LinePlotter():
    def __init__(self,
                 size=(600, 400),
                 title=None,
                 xlabel=None,
                 ylabel=None
                 ):
        self.app = QApplication([])
        self.win = pg.GraphicsLayoutWidget(title=title)
        self.win.resize(*size)
        self.win.show()

        self.plotitem = self.win.addPlot()
        self.plotitem.showGrid(x=True, y=True)
        if xlabel is not None:
            self.plotitem.setLabels(bottom=xlabel)
        if ylabel is not None:
            self.plotitem.setLabels(left=ylabel)

        self.plots = []

    def draw(self, *args):
        """
        args:
            - ydata
            - [ydata]
            - xdata, ydata
            - xdata, [ydata]
            - xdata, ydata1, ydata2
            - xdata, ydata1, ydata2, ...
        """
        xdata = ydata = None
        if len(args) == 1:
            ydata = args
        elif len(args) == 2:
            xdata, ydata = args
        else:  # len(args) > 2
            xdata = args[0]
            ydata = args[1:]

        vec = np.array(ydata)
        if len(vec.shape) == 1:
            vec = np.array([ydata])

        if xdata is None:
            xdata = np.arange(len(vec[0]))

        if len(self.plots) < len(vec):
            for _ in range(len(vec) - len(self.plots)):
                p = self.plotitem.plot()
                self.plots.append(p)

        for p, v in zip(self.plots, vec):
            p.setData(xdata, v)


if __name__ == '__main__':
    plotter = LinePlotter(title='line plotter')
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QApplication.instance().exec_()
