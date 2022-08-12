import itertools
import sys
import socket
import pickle
from typing import Any

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

        self.receiver = DataReceiver()
        self.receiver.sigData.connect(self.draw_unpack)
        self.receiver.sigClear.connect(self.clear)
        self.receiver.start()
        # TODO: QThread の適切な終了方法がわからん
        #       `QThread: Destroyed while thread is still running` と怒られてしまう
        # self.app.aboutToQuit.conncect(self.receiver.stop()) とかやると別の怒られが起きる
        # とりあえず放置。。。

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


if __name__ == '__main__':
    plotter = LinePlotter(title='line plotter')
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QApplication.instance().exec_()
