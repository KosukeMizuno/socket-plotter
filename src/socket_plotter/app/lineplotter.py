from __future__ import annotations
from typing import Any, Sequence

from PySide2.QtWidgets import QApplication
import numpy as np
import pyqtgraph as pg

from .receiver import QThreadReceiver


class LinePlotter:
    DEFAULT_SIZE = (600, 400)
    DEFAULT_WINDOW_TITLE = "Line Plotter"

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
        if attrs.get("xlabel", None):
            self.plotitem.setLabel("bottom", attrs["xlabel"])
        if attrs.get("ylabel", None):
            self.plotitem.setLabel("left", attrs["ylabel"])
        if attrs.get("windowsize", None):
            self.win.resize(*attrs["windowsize"])

    def clear(self):
        for p in self.plots:
            p.setData([], [])

    def draw_unpack(self, args: Sequence[Any]):
        """wrapper for signal communication.

        This function receives a sequence object.
        The object will be unpacked and pass to ``draw``.

        Args:
            args (Sequence[Any]): an object to be unpacked.
        """
        self.draw(*args)

    def draw(self, *dat):
        """Plot a line or lines.

        The structure of ``dat`` will be automatically determined.
        ``dat`` should be in the following forms:

        - ``ydata``
        - ``[ydata]``
        - ``xdata, ydata``
        - ``xdata, [ydata]``
        - ``xdata, ydata1, ydata2, ...``

        If socket connection is refused, a new plotter will be launched.

        Args:
            *dat: data to be plotted. See the above note.
        """
        # determine the structure of dat & extract xdata and ydata.
        xdata = ydata = None
        if len(dat) == 1:
            ydata = dat[0]
        elif len(dat) == 2:
            xdata, ydata = dat
        else:  # len(args) > 2
            xdata = dat[0]
            ydata = dat[1:]

        vec = np.array(ydata)
        if len(vec.shape) == 1:
            vec = [vec]

        if xdata is None:
            xdata = np.arange(len(vec[0]))

        # make plotitem instances if needed.
        if len(self.plots) < len(vec):
            for _ in range(len(vec) - len(self.plots)):
                p = self.plotitem.plot()
                self.plots.append(p)

        # draw lines
        self.clear()
        for i, (p, v) in enumerate(zip(self.plots, vec)):
            p.setPen(pg.mkPen(i, hues=max(len(vec), 9)))
            p.setData(xdata, v)
