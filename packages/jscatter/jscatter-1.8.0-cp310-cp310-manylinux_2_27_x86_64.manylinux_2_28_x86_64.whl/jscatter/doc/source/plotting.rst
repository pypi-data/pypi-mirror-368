Plotting
========
.. currentmodule::jscatter

The intention is to allow fast/easy plotting (one command to plot) with some convenience
function in relation to dataArrays and in a non blocking mode of matplotlib.

**XmGrace**
 A high-level Python interface to the Grace plotting package XmGrace

 One line command plotting: plot of numpy arrays and dataArrays without
 predefining Data or Symbol objects.
 symbol, line and error are defined by list arguments as line=[1,0.5,3]

 How to write **special symbols** and more see :ref:`Tips`.

**mpl**
 This is a rudimentary interface to matplotlib to use dataArrays/sasImage easier.
 The standard way to use matplotlib is full available without using this module and
 recommended for more complicated use cases. Nevertheless the source can be used as template
 to be adapted.

.. toctree::
   :maxdepth: 2

   Using GracePlot <GracePlot>
   Using matplotlib <mpl>

This is an example using **GracePlot**

.. image:: ../../examples/images/Graceexample.jpg
     :width: 50 %
     :align: center
     :alt: Graceexample

This is an example using **mpl**

.. image:: ../../examples/images/lineandcontourImage.jpg
    :align: center
    :width: 50 %
    :alt: lines and contourImage


|
|
|
|
|



----