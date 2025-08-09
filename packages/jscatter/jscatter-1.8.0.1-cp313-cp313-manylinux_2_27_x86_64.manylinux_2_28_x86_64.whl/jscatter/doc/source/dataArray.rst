dataArray
=========

.. currentmodule:: jscatter.dataarray

.. include:: ../../dataarray.py
    :start-after: **dataArray**
    :end-before:  **dataList**

dataArray Class
---------------
.. autosummary::
    dataArray

- dataArray creating by data=js.dA('filename.dat') or from numpy arrays.
- Array columns can be accessed as automatic generated attributes like *.X,.Y,.eY* (see protectedNames).
  or by indexing as ``data[0]``
- Corresponding column indices are set by :py:meth:`~dataArray.setColumnIndex` (default X,Y,eY = 0,1,2).
- Multidimensional fitting of  1D,2D,3D (.X,.Z,.W) data.
  .Y are used as function values at coordinates [.X,.Z,.W] in fitting.
- Attributes can be set like:  data.aName= 1.2345
- Methods are used as data.methodname(arguments)

Attribute Methods
-----------------
.. autosummary::
        protectedNames

.. autosummary::

        ~dataArray.showattr
        ~dataArray.attr
        ~dataArray.getfromcomment
        ~dataArray.extract_comm
        ~dataArray.resumeAttrTxt
        ~dataArray.setattr
        ~dataArray.setColumnIndex
        ~dataArray.columnIndex
        ~dataArray.name
        ~dataArray.array
        ~dataArray.argmax
        ~dataArray.argmin

Fit Methods
-----------
**Least square fit and Bayes**

.. autosummary::

        ~dataArray.fit
        ~dataArray.modelValues
        ~dataArray.estimateError
        ~dataArray.refineFit
        ~dataArray.getBayesSampler
        ~dataArray.setLimit
        ~dataArray.hasLimit
        ~dataArray.setConstrain
        ~dataArray.hasConstrain
        ~dataArray.makeErrPlot
        ~dataArray.makeNewErrPlot
        ~dataArray.killErrPlot
        ~dataArray.detachErrPlot
        ~dataArray.showlastErrPlot
        ~dataArray.savelastErrPlot
        ~dataArray.simulate

**Prediction**

.. autosummary::

        ~dataArray.polyfit
        ~dataArray.interpolate
        ~dataArray.interpAll
        ~dataArray.interp

Housekeeping Methods
--------------------
.. autosummary::

        ~dataArray.savetxt
        ~dataArray.isort
        ~dataArray.where
        ~dataArray.prune
        ~dataArray.merge
        ~dataArray.concatenate
        ~dataArray.addZeroColumns
        ~dataArray.addColumn
        ~dataArray.nakedCopy
        ~dataArray.regrid

Convenience
-----------
.. autosummary::
    
        zeros
        ones
        fromFunction

-----

.. autodata:: jscatter.dataarray.protectedNames

.. autoclass:: jscatter.dataarray.dataArray
    :members:
    :inherited-members:
    :show-inheritance:
    :exclude-members: strides

.. automethod:: jscatter.dataarray.zeros
.. automethod:: jscatter.dataarray.ones
.. automethod:: jscatter.dataarray.fromFunction

