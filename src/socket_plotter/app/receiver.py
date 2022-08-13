from __future__ import annotations
from typing import Any

import socket
import pickle

from PySide2 import QtCore


class QThreadReceiver(QtCore.QThread):
    """
    1. 接続を受けたら、以下のようなdict (header) を受け取る
        {'size': int, 'type': Literal['data', 'attr', 'ping']}
        - type==ping なら何もせずに次の接続をまつ
        - TODO: headerはjsonで受けて、データ自体もjsonで受けるモードを作りたい。現状だとpython限定だしバージョン合わせの問題が出るかも
    2. `A header was received.` と返す
    3. (1)で受けたサイズだけデータを受け取る
    4. type==data ならsigDataでui側へ渡す。type==attrならsigAttrでui側へ渡す

    途中でエラーしたら sigErrorを発してui側へ通知
    """
    buffer_size = 2048
    timeout = 0.1

    sigData = QtCore.Signal(object)
    sigAttr = QtCore.Signal(object)
    sigError = QtCore.Signal()

    def __init__(self, addr: str, port: int, parent=None) -> None:
        super().__init__(parent)

        self._mutex = QtCore.QMutex()
        self._flg_listen = True  # これがTrueの間は受け付け続ける

        self.addr_port = (addr, port)

    def stop(self) -> None:
        with QtCore.QMutexLocker(self._mutex):
            self._flg_listen = False

    def run(self) -> None:
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(self.addr_port)
        self.s.listen(1)
        self.s.settimeout(self.timeout)

        while self._flg_listen:
            try:
                type, dat = self._recv()
                if type == 'data':
                    self.sigData.emit(dat)
                elif type == 'attr':
                    self.sigAttr.emit(dat)
                elif type == 'ping':
                    pass
                else:
                    self.sigError.emit()

            except socket.timeout:
                continue
            except ConnectionError:
                self.sigError.emit()
            except pickle.UnpicklingError:
                self.sigError.emit()

        self.s.close()

    def _recv(self) -> tuple[str, Any]:
        conn, _ = self.s.accept()
        with conn:
            header_bytes = conn.recv(self.buffer_size)
            header = pickle.loads(header_bytes)
            if header['type'] == 'ping':
                return 'ping', None

            conn.send(b'A header was received.')

            databuf = bytearray(header['size'])
            conn.recv_into(databuf)

        return header['type'], pickle.loads(databuf)
