import sys
import socket
import pickle

import numpy as np
import pyqtgraph as pg

from PySide2 import QtCore
from PySide2.QtCore import QThread
from PySide2.QtWidgets import QApplication


class DataReceiver(QThread):
    addr = '127.0.0.1'
    port = 7707
    buffer_size = 4096

    sigData = QtCore.Signal(object)
    sigClear = QtCore.Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.mutex = QtCore.QMutex()
        self._stop_flg = False

    def stop(self):
        with QtCore.QMutexLocker(self.mutex):
            self._stop_flg = True

    def run(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.addr, self.port))
        self.s.listen(1)
        self.s.settimeout(0.1)

        while not self._stop_flg:
            try:
                v = self._recv()
                self.sigData.emit(v)
            except socket.timeout:
                continue
            except ConnectionResetError:
                self.sigClear.emit()
            except ConnectionAbortedError:
                self.sigClear.emit()
            except pickle.UnpicklingError:
                self.sigClear.emit()

        self.s.close()

    def _recv(self):
        try:
            conn, _ = self.s.accept()
        except socket.timeout:
            raise
        # print("accepted:", (conn, addr))

        with conn:
            header_bytes = conn.recv(self.buffer_size)
            header = pickle.loads(header_bytes)
            # print(header)

            conn.send(b'size was received.')

            databuf = bytearray(header['size'])
            conn.recv_into(databuf)
            # print('received.')

        try:
            v = pickle.loads(databuf)
        except pickle.UnpicklingError:
            raise

        return v


class ImagePlotter():
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

        self.imageitem = pg.ImageItem()
        self.imageitem.setOpts(axisOrder='row-major')

        self.viewbox = self.win.addViewBox()
        self.viewbox.setAspectLocked(lock=True)
        self.viewbox.addItem(self.imageitem)

        self.plotitem = pg.PlotItem(viewBox=self.viewbox)
        self.plotitem.showGrid(x=True, y=True)
        self.plotitem.setAspectLocked(lock=False)
        if xlabel is not None:
            self.plotitem.setLabels(bottom=xlabel)
        if ylabel is not None:
            self.plotitem.setLabels(left=ylabel)
        self.win.addItem(self.plotitem)

        self.histgramlutitem = pg.HistogramLUTItem(self.imageitem)
        self.win.addItem(self.histgramlutitem)

        self.receiver = DataReceiver()
        self.receiver.sigData.connect(self.draw)
        self.receiver.sigClear.connect(self.clear)
        self.receiver.start()
        # TODO: QThread の適切な終了方法がわからん
        #       `QThread: Destroyed while thread is still running` と怒られてしまう
        # self.app.aboutToQuit.conncect(self.receiver.stop()) とかやると別の怒られが起きる
        # とりあえず放置。。。

        self.draw(np.random.randn(20, 100))

    def clear(self):
        self.imageitem.clear()

    def draw(self, img):
        """
        args:
            - imagedata
        """
        vec = np.array(img)
        if len(vec.shape) != 2:
            self.clear()
            return

        self.imageitem.setImage(vec)


if __name__ == '__main__':
    plotter = ImagePlotter(title='line plotter')
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QApplication.instance().exec_()
