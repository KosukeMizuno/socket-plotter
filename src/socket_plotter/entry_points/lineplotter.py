import sys
import argparse

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication

from socket_plotter.api import DEFAULT_ADDR, DEFAULT_PORT_LINEPLOTTER
from socket_plotter.app.lineplotter import LinePlotter


def run(addr: str, port: int):
    _ = LinePlotter(addr, port)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
        QApplication.instance().exec_()


def main():
    parser = argparse.ArgumentParser(description="launch a line plotter")
    parser.add_argument("--addr", default=DEFAULT_ADDR, help=f"default={DEFAULT_ADDR}")
    parser.add_argument(
        "--port",
        default=DEFAULT_PORT_LINEPLOTTER,
        type=int,
        help=f"default={DEFAULT_PORT_LINEPLOTTER}",
    )

    args = parser.parse_args()
    run(args.addr, args.port)


if __name__ == "__main__":
    main()
