import jscatter as js
import numpy as np
import random
gp=js.graceplot

x = np.r_[1:11]
y = x
dy = map(lambda x: random.random() * 2., x)
labels = ['pt1', 'pt2', 'Iridium', 'Na', 'Ti', 'hydrogen', 'Mo ' + "1.23e3", 'Ta',
          'pokemon',
          'digital']

p = js.grace(width=2, height=1.5)  # A grace session opens

# original idea to create symbols and lines and data object
s1 = gp.Symbol(symbol=gp.symbols.square, fillcolor=gp.colors.cyan)
l1 = gp.Line(type=gp.lines.none)

d1 = gp.DataXYDY(x=x, y=y, dy=dy, symbol=s1, line=l1)

g = p[0]
g.xaxis(min=0, max=12)
g.yaxis(min=0, max=12)

g.plot(d1, autoscale=False)

for i in range(len(labels)):
    g.text('  ' + labels[i], x[i], y[i], color=gp.colors.violet, charsize=1.2)

g.line(x1=3, y1=1, x2=8, y2=2, linewidth=3, color=gp.colors.green4)
p.save('grace3.png')
