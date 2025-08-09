import jscatter as js
import numpy as np
gp=js.graceplot

# make some data
x1 = np.r_[0:10:0.1]
y1 = np.sin(x1)
y2 = np.cos(x1)

p = js.grace()  # A grace session opens
p.multi(2, 1)
# the SHORT way
p.plot(x1, y1, sy=[1, 0.5, 2])
p.plot(x1, y2, sy=[1, 0.5, 4])
# the long old way

# original idea to create symbols and lines and data object
l1 = gp.Line(type=gp.lines.none)  # or l1=Line(type=0)
d2 = gp.Data(x=x1, y=y1, bsymbol=gp.Symbol(symbol=gp.symbols.circle, fillcolor=gp.colors.red), line=l1)
d3 = gp.Data(x=x1, y=y2, symbol=gp.Symbol(symbol=gp.symbols.circle, fillcolor=gp.colors.blue), line=l1)

g = p[1]
g.plot(d2, d3)
g.xaxis(label=gp.Label('X axis', font=5, charsize=1.5),
        tick=gp.Tick(majorgrid=True, majorlinestyle=gp.lines.dashed, majorcolor=gp.colors.blue,
                     minorgrid=True, minorlinestyle=gp.lines.dotted, minorcolor=gp.colors.blue))
g.yaxis(tick=gp.Tick(majorgrid=True, majorlinestyle=gp.lines.dashed, majorcolor=gp.colors.blue,
                     minorgrid=True, minorlinestyle=gp.lines.dotted, minorcolor=gp.colors.blue))

p[0].title('grace2 example')
p.save('grace2.png')
