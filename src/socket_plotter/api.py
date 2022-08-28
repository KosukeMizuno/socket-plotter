"""APIs for socket-plotter

- This module exposes some functions to launch plotter GUIs (if needed) and to send data.
- A python executable to launch a GUI can be assign
  with ``SOCKETPLOTTER_PYTHON_EXECUTABLE`` environment variable.
  If it's not set, the GUI is launched with the same executable calling the api functions.
"""
from __future__ import annotations
from typing import Optional, Any

import os
import sys
import socket
import json
import pickle
import subprocess
from pathlib import Path

DEFAULT_ADDR = "127.0.0.1"
DEFAULT_PORT_LINEPLOTTER = 8765
DEFAULT_PORT_IMAGEPLOTTER = 8766


def plot_lines(
    *dat,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    windowsize: Optional[tuple[int, int]] = None,
    addr: str = DEFAULT_ADDR,
    port: int = DEFAULT_PORT_LINEPLOTTER,
):
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
        xlabel (str, optional): Defaults to None.
        ylabel (str, optional): Defaults to None.
        windowsize (tuple[int, int], optional): Defaults to None.
        addr (str): Address of the plotter. Defaults to DEFAULT_ADDR.
        port (int): Port of the plotter. Defaults to DEFAULT_PORT_LINEPLOTTER.
    """
    _ping_or_launch_lineplotter(addr, port)

    _send_data(dat, addr, port)

    attrs = dict(xlabel=xlabel, ylabel=ylabel, windowsize=windowsize)
    _send_attrs(addr, port, attrs)


def plot_image(
    img,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    windowsize: Optional[tuple[int, int]] = None,
    addr: str = DEFAULT_ADDR,
    port: int = DEFAULT_PORT_IMAGEPLOTTER,
):
    """Plot an image.

    If socket connection is refused, a new plotter will be launched.

    Args:
        img (2d-ndarray): image to be plotted.
        xlabel (str, optional): Defaults to None.
        ylabel (str, optional): Defaults to None.
        windowsize (tuple[int, int], optional): Defaults to None.
        addr (str): Address of the plotter. Defaults to DEFAULT_ADDR.
        port (int): Port of the plotter. Defaults to DEFAULT_PORT_IMAGEPLOTTER.

    TODO:
        xaxis, yaxis を受け入れる
    """
    _ping_or_launch_imageplotter(addr, port)

    _send_data(img, addr, port)

    attrs = dict(xlabel=xlabel, ylabel=ylabel, windowsize=windowsize)
    _send_attrs(addr, port, attrs)


def plot_image_and_lines(
    img,
    addr: str = DEFAULT_ADDR,
    port_image: int = DEFAULT_PORT_IMAGEPLOTTER,
    port_lines: int = DEFAULT_PORT_LINEPLOTTER,
):
    """Plot an image, and plot each row of the image

    If socket connection is refused, a new plotter will be launched.

    Args:
        img (2d-ndarray): image to be plotted.
        addr (str): Address of the plotter. Defaults to DEFAULT_ADDR.
        port_image (int): Port of the image plotter. Defaults to DEFAULT_PORT_IMAGEPLOTTER.
        port_lines (int): Port of the line plotter. Defaults to DEFAULT_PORT_LINEPLOTTER.

    TODO:
        xlabel,ylabelなどを受け入れる
    """
    plot_image(img, addr=addr, port=port_image)
    plot_lines(img, addr=addr, port=port_lines)


def _ping_or_launch_lineplotter(addr: str, port: int):
    """Try to connect a lineplotter. If refused, this launches a new plotter.

    Args:
        addr (str): Address of the plotter. Defaults to DEFAULT_ADDR.
        port (int): Port of the plotter. Defaults to DEFAULT_PORT_IMAGEPLOTTER.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((addr, port))
            header = json.dumps({"type": "ping"}).encode("utf-8")
            s.send(header)
    except ConnectionRefusedError:
        fn_entry = Path(__file__).parent / "entry_points/lineplotter.py"
        _ = subprocess.Popen(
            [
                _get_executable(),
                str(fn_entry.absolute()),
                "--addr",
                addr,
                "--port",
                str(port),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def _ping_or_launch_imageplotter(addr: str, port: int):
    """Try to connect an imageplotter. If refused, this launches a new plotter.

    Args:
        addr (str): Address of the plotter. Defaults to DEFAULT_ADDR.
        port (int): Port of the plotter. Defaults to DEFAULT_PORT_IMAGEPLOTTER.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((addr, port))
            header = json.dumps({"type": "ping"}).encode("utf-8")
            s.send(header)
    except ConnectionRefusedError:
        fn_entry = Path(__file__).parent / "entry_points/imageplotter.py"
        _ = subprocess.Popen(
            [
                _get_executable(),
                str(fn_entry.absolute()),
                "--addr",
                addr,
                "--port",
                str(port),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def _send_data(v: Any, addr: str, port: int):
    """Send an object to the plotter.

    Args:
        v (Any): an object to be sent.
        addr (str): Address of the plotter.
        port (int): Port of the plotter.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((addr, port))

        data = pickle.dumps(v)
        header = json.dumps({"size": len(data), "type": "data"}).encode("utf-8")

        s.send(header)
        _ = s.recv(2048)
        s.sendall(data)


def _send_attrs(addr: str, port: int, attrs: dict):
    """Send attributes to the plotter.

    If all items of ``attrs`` are None, this function does nothing.

    Args:
        addr (str): Address of the plotter.
        port (int): Port of the plotter.
        attrs (dict): Attributes to be sent.
    """
    if not any(attrs.values()):
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((addr, port))

        data = pickle.dumps(attrs)
        header = json.dumps({"size": len(data), "type": "attr"}).encode("utf-8")

        s.send(header)
        _ = s.recv(2048)
        s.sendall(data)


def _get_executable() -> str:
    """Get a python executable to launch a plotter.

    Returns:
        str: filename to the python executable
    """
    KEY_EXE = "SOCKETPLOTTER_PYTHON_EXECUTABLE"
    if KEY_EXE in os.environ:
        p = Path(os.environ[KEY_EXE])
        if p.exists():
            return str(p)

    return sys.executable
