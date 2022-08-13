from __future__ import annotations

import sys
import socket
import pickle
import subprocess
from pathlib import Path

DEFAULT_ADDR_LINEPLOTTER = '127.0.0.1'
DEFAULT_PORT_LINEPLOTTER = 8765

DEFAULT_ADDR_IMAGEPLOTTER = '127.0.0.1'
DEFAULT_PORT_IMAGEPLOTTER = 8766


def plot_lines(*args,
               addr: str = DEFAULT_ADDR_LINEPLOTTER,
               port: int = DEFAULT_PORT_LINEPLOTTER):
    """
    args:
        - ydata
        - [ydata]
        - xdata, ydata
        - xdata, [ydata]
        - xdata, ydata1, ydata2
        - xdata, ydata1, ydata2, ...

    TODO: 上記のように受け付けてないので要修正, ydataをそのまま送る分にはOK

    # TODO: xlabel, ylabel, title などを設定できるようにしたい
    """
    _ping_or_launch_lineplotter(addr, port)
    _send_data(args, addr, port)


def plot_image(img,
               addr: str = DEFAULT_ADDR_IMAGEPLOTTER,
               port: int = DEFAULT_PORT_IMAGEPLOTTER):
    pass


def _ping_or_launch_lineplotter(addr: str, port: int):
    """lineplotterがあるか確認、起動してなければ起動する
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((addr, port))
            header = pickle.dumps({'type': 'ping'})
            s.send(header)
    except ConnectionRefusedError:
        fn_entry = Path(__file__).parent / 'entry_points/lineplotter.py'
        _ = subprocess.Popen([sys.executable, fn_entry.absolute(),
                              '--addr', addr, '--port', str(port)])


def _ping_or_launch_imagplotter(addr: str, port: int):
    """imageplotterがあるか確認、起動してなければ起動する
    """
    pass


def _send_data(v, addr: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((addr, port))

        data = pickle.dumps(v)
        header = pickle.dumps({'size': len(data), 'type': 'data'})

        s.send(header)
        _ = s.recv(2048)
        s.sendall(data)


if __name__ == '__main__':
    # test code
    import numpy as np
    plot_lines(np.random.randn(100))
