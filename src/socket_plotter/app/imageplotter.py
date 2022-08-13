from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide2.QtWidgets import QApplication

from .receiver import QThreadReceiver


class ImagePlotter():
    DEFAULT_SIZE = (600, 400)
    DEFAULT_TITLE = 'Image Plotter'

    def __init__(self, addr: str, port: int):
        self.app = QApplication([])
        self.win = pg.GraphicsLayoutWidget(title=self.DEFAULT_TITLE)
        self.win.resize(*self.DEFAULT_SIZE)
        self.win.show()

        self.imageitem = pg.ImageItem()
        self.imageitem.setOpts(axisOrder='row-major')

        self.viewbox = self.win.addViewBox()
        self.viewbox.setAspectLocked(lock=True)
        self.viewbox.addItem(self.imageitem)

        self.plotitem = pg.PlotItem(viewBox=self.viewbox)
        self.plotitem.showGrid(x=True, y=True)
        self.plotitem.setAspectLocked(lock=False)
        self.win.addItem(self.plotitem)

        self.histgramlutitem = pg.HistogramLUTItem(self.imageitem)
        self.win.addItem(self.histgramlutitem)

        # TODO: QThread の適切な終了方法がわからん
        #       `QThread: Destroyed while thread is still running` と怒られてしまう
        # self.app.aboutToQuit.conncect(self.receiver.stop()) とかやると別の怒られが起きる
        # とりあえず放置。。。
        self.receiver = QThreadReceiver(addr, port)
        self.receiver.sigData.connect(self.draw)
        self.receiver.sigAttr.connect(self.set_attributes)
        self.receiver.sigError.connect(self.clear)
        self.receiver.start()

    def set_attributes(attrs):
        # TODO: xlabel, ylabel, title, windowsize などを設定できるようにしたい
        raise NotImplementedError

    def clear(self):
        self.imageitem.clear()

    def draw(self, img):
        """
        args:
            - img, 2d array_like
        """
        vec = np.array(img)
        if len(vec.shape) != 2:
            self.clear()
            return

        self.imageitem.setImage(vec)
