import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Heiti TC', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

x = np.linspace(0, 4 * np.pi, 500)

fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(bottom=0.25)

A_init, omega_init, phi_init = 1.0, 1.0, 0.0

sin_line, = ax.plot(x, A_init * np.sin(omega_init * x + phi_init), 'b-', label='sin(x)')
cos_line, = ax.plot(x, A_init * np.cos(omega_init * x + phi_init), 'r-', label='cos(x)')

ax.set_xlim(0, 4 * np.pi)
ax.set_title('正弦與餘弦波形')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.grid(True)
ax.legend()

ax_A = plt.axes([0.15, 0.10, 0.70, 0.03])
ax_omega = plt.axes([0.15, 0.06, 0.70, 0.03])
ax_phi = plt.axes([0.15, 0.02, 0.70, 0.03])

slider_A = Slider(ax_A, '振幅 (A)', 0.1, 5.0, valinit=A_init)
slider_omega = Slider(ax_omega, '頻率 (ω)', 0.1, 10.0, valinit=omega_init)
slider_phi = Slider(ax_phi, '相位偏移 (φ)', 0, 2 * np.pi, valinit=phi_init)

def update(val):
    A = slider_A.val
    omega = slider_omega.val
    phi = slider_phi.val
    sin_line.set_ydata(A * np.sin(omega * x + phi))
    cos_line.set_ydata(A * np.cos(omega * x + phi))
    fig.canvas.draw_idle()

slider_A.on_changed(update)
slider_omega.on_changed(update)
slider_phi.on_changed(update)

plt.show()
