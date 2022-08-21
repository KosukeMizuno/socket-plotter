from __future__ import annotations
from typing import Any

import socket
import json
import pickle

from PySide2 import QtCore


class QThreadReceiver(QtCore.QThread):
    """
    1. 接続を受けたら、以下のようなdict (header) をjsonで受け取る
        {'size': int, 'type': Literal['data', 'data_json', 'attr', 'ping']}
        - type==ping なら何もせずに次の接続をまつ
    2. `A header was received.` と返す
    3. (1)で受けたサイズだけデータを受け取る
    4. type==(data|data_json) ならsigDataでui側へ渡す。type==attrならsigAttrでui側へ渡す
      - data|attr だったらデータをpickleで受け取る
      - data_json だった場合はデータをjsonで受け取る

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
                if type in ('data', 'data_json'):
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
            except json.JSONDecodeError:
                self.sigError.emit()

        self.s.close()

    def _recv(self) -> tuple[str, Any]:
        conn, _ = self.s.accept()
        with conn:
            header_bytes = conn.recv(self.buffer_size)
            header = json.loads(header_bytes)
            if header['type'] == 'ping':
                return 'ping', None

            # receiving body
            conn.send(b'A header was received.')

            databuf = bytearray(header['size'])
            conn.recv_into(databuf)

        if header['type'] == 'data_json':
            return header['type'], json.loads(databuf)
        else:
            return header['type'], pickle.loads(databuf)
