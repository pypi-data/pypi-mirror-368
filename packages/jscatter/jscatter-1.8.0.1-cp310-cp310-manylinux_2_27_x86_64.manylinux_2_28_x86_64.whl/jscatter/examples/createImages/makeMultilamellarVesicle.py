import numpy as np
import matplotlib.pyplot as pyplot

pyplot.ion()

fig = pyplot.figure(figsize=(10, 5))
fig.add_subplot(1, 2, 1)
fig.add_subplot(1, 2, 2)
fig.axes[1].set_xlim((-5, 5))
fig.axes[1].set_ylim((-5, 5))

fig.axes[0].set_xlim((-5, 5))
fig.axes[0].set_ylim((-5, 5))
R = 5
x = 0
y = 0
r = 0.4
X = []
Y = []
for rr in np.r_[0:2:10j]:
    phi = np.random.rand(1) * 2 * np.pi
    x = x + r * np.sin(phi)
    y = y + r * np.cos(phi)
    X.append(x)
    Y.append(y)
    R -= r + 0.1
    print(x, y, phi)
    fig.axes[1].add_artist(pyplot.Circle((x, y), R, color='b', fill=False))
    fig.axes[1].add_artist(pyplot.Circle((x, y), 0.05, color='b', fill=False))
fig.axes[1].plot(X, Y)

R = 5
x = 0
y = 0
r = 0.4
for rr in np.r_[0:2:10j]:
    phi = np.random.rand(1) * 2 * np.pi
    x = 0
    y = 0
    R -= r + 0.1
    print(x, y, phi)
    fig.axes[0].add_artist(pyplot.Circle((x, y), R, color='b', fill=False))

# fig.savefig('MultiLamellarVesicles.png')
