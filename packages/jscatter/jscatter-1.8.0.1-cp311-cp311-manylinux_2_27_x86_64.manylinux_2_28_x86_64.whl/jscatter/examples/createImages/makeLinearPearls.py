import numpy as np
import matplotlib.pyplot as pyplot
import jscatter as js

pyplot.ion()

fig = pyplot.figure(figsize=(10, 5))
fig.add_subplot(2, 1, 1)
fig.add_subplot(2, 1, 2)
fig.axes[1].set_xlim((-2, 20))
fig.axes[1].set_ylim((-2, 2))
fig.axes[0].set_xlim((-2, 20))
fig.axes[0].set_ylim((-2, 2))
fig.suptitle('linear pearls with connector', fontsize=16)
fig.axes[0].set_title('no distortion or polydispersity')
fig.axes[1].set_title('with position distortion + polydispersity')

R = 1
l = 3
y = 0
N = 4
n = 7
xpearls = np.r_[0:N] * (2 * R + l)
for p in xpearls:
    fig.axes[0].add_artist(pyplot.Circle((p, y), R, color='b', fill=False))
for p in xpearls[:-1]:
    r = l / 2 / n
    xcoils = p + R + r + 2 * r * np.r_[0:n]
    for c in xcoils:
        fig.axes[0].add_artist(pyplot.Circle((c, y), r, color='b', fill=False))

xpearls = np.r_[0:N] * (2 * R + l)
for p in xpearls:
    x, y = np.random.rand(2) * 0.5
    dR = 1 + 0.5 * (np.random.rand(1) - 0.5)
    fig.axes[1].add_artist(pyplot.Circle((p + x, y), R * dR, color='b', fill=False))
for p in xpearls[:-1]:
    r = l / 2 / n
    xcoils = p + R + r + 2 * r * np.r_[0:n]
    for c in xcoils:
        x, y = np.random.rand(2) * 0.5
        dR = 1 + 0.5 * (np.random.rand(1) - 0.5)
        fig.axes[1].add_artist(pyplot.Circle((c + x, y), r * dR, color='b', fill=False))

fig.axes[0].plot([0, 1], [0, 0], 'k--', )
fig.axes[0].text(0.5, 0.2, 'R')

fig.axes[0].plot([1, 4], [0.6, 0.6], 'k--', )
fig.axes[0].text(2, 1, 'l = n 2r')

fig.axes[0].plot([0, 5], [-1.2, -1.2], 'b--', )
fig.axes[0].text(2., -1.7, '2R+l')

# fig.savefig(js.examples.imagepath+'/linearPearlsSketch.png')
