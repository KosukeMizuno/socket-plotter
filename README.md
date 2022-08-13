# socket-plotter

Instant plotter based on `pyqtgraph` via socket communication.

[![PyPI version](https://badge.fury.io/py/socket-plotter.svg)](https://badge.fury.io/py/socket-plotter) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


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

The default ports are `8765` for lineplot and `8766` for imageplot.
The default address is `127.0.0.1`.
Other ports and address can be assigned as the following:
```python
plot_lines(xdata, ydata, addr='<address to plotter>', port=7777)
```


### screenshots

![plot lines](https://user-images.githubusercontent.com/43668684/184507049-468e1bf5-4f3f-4cf9-87b1-f87875cbb507.png)

![plot image](https://user-images.githubusercontent.com/43668684/184507102-fb593784-0413-4a1c-90e3-c00887a1ff1f.png)


### dependency

- PySide2
- pyqtgraph
- numpy

## Change log
### [0.1.0]
- released

