import numpy as np
import matplotlib.pyplot as plt

x = np.arange(0, 4, 0.2)

y1 = np.cos(np.pi * x)
y2 = np.cos(2 * np.pi * x)

plt.subplot(1, 2, 1)
plt.plot(x, y1, 'g-')

plt.subplot(1, 2, 2)
plt.plot(x, y2, 'm:')

plt.show()
