import jscatter as js
import numpy as np
gp=js.graceplot

# original idea to create symbols and lines and data object
# make some data
x = np.r_[0:10]
y = np.r_[0:10]
y2 = np.r_[0:10] + 3

p = js.grace()  # A grace session opens
p.multi(2, 1)
# the new SHORT way to make the plot
p.plot(x, y, sy=[1, 0.5, 2, 2], li=0)
p.plot(x, y2, sy=[1, 0.5, 3, 3], li=0)

# the long way
# make lines and symbols
s1 = gp.Symbol(symbol=gp.symbols.circle, fillcolor=gp.colors.red)
l1 = gp.Line(type=gp.lines.none)
# create Data object
d1 = gp.Data(x=x, y=y, symbol=s1, line=l1)

g = p[1]
g.plot(d1)
g.plot(x, y2)
# but do NOT mix it like g.plot(d1,x,y2)

# add some text and labels
g.text('test', .51, .51, color=2)
p.title('Graph Title')
g.yaxis(label=gp.Label('Interesting Ydata', font=2, charsize=1.5))
g.xaxis(label=gp.Label('X axis', font=5, charsize=1.5))

p.save('grace1.png')
