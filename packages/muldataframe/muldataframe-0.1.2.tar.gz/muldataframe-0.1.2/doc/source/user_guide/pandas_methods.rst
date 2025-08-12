Pandas methods
================

The first argument to the ``.call`` method of MulSeries or MulDataFrame can also be a string. The string must be a valid method name of ``pandas.Series`` (for MulSeries) or ``pandas.DataFrame`` (for MulDataFrame). The method is called on the values series or dataframe internally to get the return value. If the return value is a ``pandas.Series`` or ``pandas.DataFrame`` object, it is used as the values series or dataframe to construct the final return value of the ``.call`` method (See :doc:`call method <call_method>`).

>>> mf
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
a  1  2   a  1  2
b  3  6   b  8  9
b  5  6   b  8  7
>>> mf.call('sum')
(2,)     Series([], Name: sum, dtype: object)
-------  --------------------------------------
   f  g     sum
c  5  7  c   17
d  3  6  d   18

In the above example, the ``sum`` method of the values dataframe is called internally to get the value series of the call method's return value.

.. _pandas_methods_attr:

All the pandas methods including some special methods (see operations???) have been added as attributes to the MulDataFrame or MulSeries using the call method. When you run ``mf.sum``, ``mf.call('sum')`` is executed under the hood.

>>> mf.sum()
(2,)     Series([], Name: sum, dtype: object)
-------  --------------------------------------
   f  g     sum
c  5  7  c   17
d  3  6  d   18

As expalined in :doc:`call method <call_method>`, only :ref:`proper_function` are valid input to the call method. Similarly, only pandas methods that are proper functions can be called on the MulSeries or MulDataFrame without error. As a result, some pandas methods (e.g. ``.value_counts``), despite their availability to MulSeries or MulDataFrame, do not work.

>>> mf.value_counts('c')
ValueError

It is better to use ``mf.ds.value_counts('c')`` in this case.

Of note, pandas methods added to MulSeries or MulDataFrame using the call method **are not listed in the API**. Users could read the pandas API documentation to learn their usage and determine whether they are proper functions. All the methods listed in the MulDataFrame API are rewrittened ones not borrowed from pandas. 





