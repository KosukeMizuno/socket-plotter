from __future__ import annotations
from audioop import add
from typing import Optional

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
               xlabel: Optional[str] = None, ylabel: Optional[str] = None,
               windowsize: Optional[tuple[int, int]] = None,
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

    TODO: 複数ラインを受けたときに適切に色を変えてプロットしたい
    """
    _ping_or_launch_lineplotter(addr, port)

    _send_data(args, addr, port)

    attrs = dict(xlabel=xlabel, ylabel=ylabel, windowsize=windowsize)
    _send_attrs(addr, port, attrs)


def plot_image(img,
               xlabel: Optional[str] = None, ylabel: Optional[str] = None,
               windowsize: Optional[tuple[int, int]] = None,
               addr: str = DEFAULT_ADDR_IMAGEPLOTTER,
               port: int = DEFAULT_PORT_IMAGEPLOTTER):
    """Plot an image

    attrs:
    - img, 2d array_like

    TODO: xaxis, yaxisを受け入れる
    """
    _ping_or_launch_imagplotter(addr, port)

    _send_data(img, addr, port)

    attrs = dict(xlabel=xlabel, ylabel=ylabel, windowsize=windowsize)
    _send_attrs(addr, port, attrs)


def plot_image_with_traces(img,
                           xlabel: Optional[str] = None, ylabel: Optional[str] = None,
                           windowsize: Optional[tuple[int, int]] = None,
                           addr: str = DEFAULT_ADDR_IMAGEPLOTTER,
                           port: int = DEFAULT_PORT_IMAGEPLOTTER):
    """Plot an image, and plot each row of the image
    """
    plot_image(img, xlabel=xlabel, ylabel=ylabel, windowsize=windowsize,
               addr=addr, port=port)
    plot_lines(img, xlabel=xlabel,
               addr=addr, port=port)


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
                              '--addr', addr, '--port', str(port)],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)


def _ping_or_launch_imagplotter(addr: str, port: int):
    """imageplotterがあるか確認、起動してなければ起動する
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((addr, port))
            header = pickle.dumps({'type': 'ping'})
            s.send(header)
    except ConnectionRefusedError:
        fn_entry = Path(__file__).parent / 'entry_points/imageplotter.py'
        _ = subprocess.Popen([sys.executable, fn_entry.absolute(),
                              '--addr', addr, '--port', str(port)],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)


def _send_data(v, addr: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((addr, port))

        data = pickle.dumps(v)
        header = pickle.dumps({'size': len(data), 'type': 'data'})

        s.send(header)
        _ = s.recv(2048)
        s.sendall(data)


def _send_attrs(addr: str, port: int, attrs: dict):
    if not any(attrs.values()):
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((addr, port))

        data = pickle.dumps(attrs)
        header = pickle.dumps({'size': len(data), 'type': 'attr'})

        s.send(header)
        _ = s.recv(2048)
        s.sendall(data)
