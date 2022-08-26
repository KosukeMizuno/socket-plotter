from __future__ import annotations
from typing import Any

import socket
import json
import pickle

from PySide2 import QtCore


class QThreadReceiver(QtCore.QThread):
    """QThread as a socket-receiver

    The communication protocol is as the followings:

    1. Wait a connection
    2. Receive a header in json format
       ````json
       {
         "size": int,
         "type": Literal['data', 'data_json', 'attr', 'ping']
       }
       ````
       If `type==ping`, do nothing. Go to (1).
    3. Return a string, `A header was received.`
    4. Receive `size` bytes.
       If `type==data_json`, a json-formatted data is coming.
       Otherwise, the incoming object is deserialized by `pickle.loads`.

    When the above protocol finishes properly, the received object will
    be passed to the received object to the plotter.
    - If `type==data or data_json`, using `sigData`.
    - If `type==attr`, using `sigAttr`.

    When an error occurs during a protocol, `sigError` will be emitted.
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
        """Communicate once.

        Returns:
            tuple[protocol type (str), incoming object (Any)]
        """
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
