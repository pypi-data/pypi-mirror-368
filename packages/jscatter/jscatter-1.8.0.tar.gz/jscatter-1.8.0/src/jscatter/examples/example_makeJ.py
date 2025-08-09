import jscatter as js
import numpy as np

# creates a scatter plot with a J = jscatter
p = js.grace(1, 1)
p.xaxis(min=0, max=1, label='Jscatter', charsize=1.7)
p.yaxis(min=0, max=1, label='Jscatter', charsize=1.7)
# p.save('./Jscatter%.2g.png' %(10),size=(200/300,200/300))

for ii in range(11, 30):
    j1 = []
    j2 = []
    j3 = []
    o = []
    for x, y in np.random.rand(200, 2):
        r = ((x - 0.5) ** 2 + (y - 0.3) ** 2) ** 0.5
        if (x > 0.2) and (x < 0.8) and 1 > y > 0.8:
            j1.append([x, y])
        elif (x > 0.6) and (x < 0.8) and 0.8 > y > 0.3:
            j2.append([x, y])
        elif (r < 0.6 / 2) and (r > 0.25 / 2) and y < 0.3:
            j3.append([x, y])
        else:
            o.append([x, y])
    p.plot(np.array(j1).T, sy=[1, 0.7, 2, 2])
    p.plot(np.array(j2).T, sy=[2, 0.7, 9, 9])
    p.plot(np.array(j3).T, sy=[5, 0.7, 4, 4])
    p.plot(np.array(o).T, sy=[9, 0.7, 11, 11])
    p.save('./Jscatter%.2g.png' % ii, size=(200/300, 200/300))

for i in np.r_[0:11:]:
    p.xaxis(min=0 + i / 10., max=1 + i / 10.)
    p.save('./Jscatter%.2g.png' % (i + ii), size=(200/300, 200/300))
import os

try:
    os.system("convert -delay 40 -resize 200x200 -layers optimize -loop 0 Jscatter??.png Jscatter.gif")
except:
    pass
p.xaxis(min=0., max=1)
