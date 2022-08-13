from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide2.QtWidgets import QApplication

from .receiver import QThreadReceiver


class LinePlotter():
    DEFAULT_SIZE = (600, 400)
    DEFAULT_WINDOW_TITLE = 'Line Plotter'

    def __init__(self, addr: str, port: int):
        self.app = QApplication([])
        self.win = pg.GraphicsLayoutWidget(title=self.DEFAULT_WINDOW_TITLE)
        self.win.resize(*self.DEFAULT_SIZE)
        self.win.show()

        self.plotitem: pg.PlotItem = self.win.addPlot()
        self.plotitem.showGrid(x=True, y=True)
        self.plots: list[pg.PlotDataItem] = []

        # TODO: QThread の適切な終了方法がわからん
        #       `QThread: Destroyed while thread is still running` と怒られてしまう
        # self.app.aboutToQuit.conncect(self.receiver.stop()) とかやると別の怒られが起きる
        # とりあえず放置。。。
        self.receiver = QThreadReceiver(addr, port)
        self.receiver.sigData.connect(self.draw_unpack)
        self.receiver.sigAttr.connect(self.set_attributes)
        self.receiver.sigError.connect(self.clear)
        self.receiver.start()

    def set_attributes(self, attrs: dict):
        if attrs.get('xlabel', None):
            self.plotitem.setLabel('bottom', attrs['xlabel'])
        if attrs.get('ylabel', None):
            self.plotitem.setLabel('left', attrs['ylabel'])
        if attrs.get('windowsize', None):
            self.win.resize(*attrs['windowsize'])

    def draw_unpack(self, args):
        self.draw(*args)

    def clear(self):
        for p in self.plots:
            p.setData([], [])

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
