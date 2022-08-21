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
