dataList
========

.. currentmodule:: jscatter.dataarray

.. include:: ../../dataarray.py
    :start-after: **dataList**
    :end-before: _end_


dataList Class
--------------
.. autosummary::
    dataList

- dataList creating by dataL=js.dL('filename.dat') or from numpy arrays.
- List columns can be accessed as automatic generated attributes like *.X,.Y,.eY* (see protectedNames).
  or by indexing as *dataL[:,0] -> .X * for all list elements.
- Corresponding column indices are set by :py:meth:`~dataList.setColumnIndex` (default X,Y,eY = 0,1,2).
- Multidimensional fitting of  1D,2D,3D (.X,.Z,.W) data including additional attributes.
  .Y (scalar) are used as function values at coordinates.
- Attributes can be set like:  dataL.aName= 1.2345 or dataL[2].aName= 1.2345
- Individual elements and dataArray methods can be accessed by indexing data[2].bName
- Methods are used as dataL.methodname(arguments)


Attribute Methods
-----------------
.. autosummary::

      ~dataList.attr
      ~dataList.dlattr
      ~dataList.commonAttr
      ~dataList.dtype
      ~dataList.names
      ~dataList.whoHasAttributes
      ~dataList.showattr

Fit Methods
-----------
**Least square fit and Bayes**

.. autosummary::
       
      ~dataList.fit
      ~dataList.modelValues
      ~dataList.estimateError
      ~dataList.refineFit
      ~dataList.getBayesSampler
      ~dataList.setLimit
      ~dataList.hasLimit
      ~dataList.setConstrain
      ~dataList.hasConstrain
      ~dataList.makeErrPlot
      ~dataList.makeNewErrPlot
      ~dataList.detachErrPlot
      ~dataList.killErrPlot
      ~dataList.showlastErrPlot
      ~dataList.errPlot
      ~dataList.savelastErrPlot
      ~dataList.simulate

**Prediction**

.. autosummary::

      ~dataList.interpolate
      ~dataList.polyfit
      ~dataList.extrapolate
      ~dataList.bispline

Housekeeping Methods
--------------------
.. autosummary::

      ~dataList.savetxt
      ~dataList.setColumnIndex
      ~dataList.append
      ~dataList.extend
      ~dataList.insert
      ~dataList.prune
      ~dataList.sort
      ~dataList.reverse
      ~dataList.delete
      ~dataList.nakedCopy
      ~dataList.extractAttribut
      ~dataList.filter
      ~dataList.index
      ~dataList.merge
      ~dataList.mergeAttribut
      ~dataList.pop
      ~dataList.copyattr2elements
      ~dataList.getfromcomment
      ~dataList.transposeAttribute

  
-----
   
.. autoclass:: jscatter.dataarray.dataList
    :members:
    :inherited-members:
    :undoc-members:
    :show-inheritance:
  
  