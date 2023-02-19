# socket-plotter

Instant plotter based on `pyqtgraph` via socket communication.

[![PyPI version](https://badge.fury.io/py/socket-plotter.svg)](https://badge.fury.io/py/socket-plotter) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


## Installation

### with pipx

1. Install CLI commands.
    - `pipx install socket-plotter[pyside]`
2. Install in python environments where you want to use this library
    - activate your environment
    - `pip install socket-plotter`


## Usage

```python
from socket_plotter import plot_lines, plot_image, plot_image_and_lines
import numpy as np

# for line plot
xdata = np.arange(100)
ydata = np.random.randn(100)
plot_lines(xdata, ydata)

# for image plot
img = np.random.randn(100, 100)
plot_image(img)

# for both, the image and each row of the image are displayed.
img = np.random.randn(100, 100)
plot_image_and_lines(img)
```

The above three functions check if a plotter process exists.
If needed, a new plotter process will be launched before plotting.
You can specify your python executable to launch plotter GUIs via an environment variable `SOCKETPLOTTER_PYTHON_EXECUTABLE`.


### Launch via command line interface

You can launch them as executables.
Note that in this case `SOCKETPLOTTER_PYTHON_EXECUTABLE` will be ignore.
The python interpreter in the installed environment will be used.

```sh
# launch it in background
$ socket_image_plotter &
$ socket_line_plotter &
```


### Addresses and ports

The default ports are `8765` for lineplot and `8766` for imageplot.
The default address is `127.0.0.1`.
Other ports and address can be assigned as the following:
```python
plot_lines(xdata, ydata, addr='<address to plotter>', port=7777)
```


### screenshots

![plot lines](https://user-images.githubusercontent.com/43668684/184507049-468e1bf5-4f3f-4cf9-87b1-f87875cbb507.png)

![plot image](https://user-images.githubusercontent.com/43668684/184507102-fb593784-0413-4a1c-90e3-c00887a1ff1f.png)


## Change log

### [0.1.4]
- refine docstrings
- add entrypoints via CLI

### [0.1.3]
- headers should be json-formatted.
- implement json-based data transfer

### [0.1.2]
- executable switch via `SOCKETPLOTTER_PYTHON_EXECUTABLE`

### [0.1.1]
- removed PySide2 from `install_requires` to avoid automatic installation by package managers for compatibility for pip and anaconda environments

### [0.1.0]
- released


## TODOs

- QThreadの適切な終了方法がよくわからないので終了時にエラーメッセージが出る
- socketのやりとりがキモいので修正したい

