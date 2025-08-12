Numpy functions
==================
Similar to :ref:`pandas methods <pandas_methods_attr>`, all numpy functions in the main namespace have been added as methods to MulDataFrame and MulSeries using the :doc:`call method <call_method>`. For exmaple, ``np.log1p`` is added but ``numpy.linalg.matmul`` is not. There is some overlap between numpy functions and pandas methods. In this case, pandas methods take precedence over numpy functions.

>>> mf
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
a  1  2   a  1  2
b  3  6   b  8  9
b  5  6   b  8  7
>>> mf.min()
(2,)     Series([], Name: min, dtype: object)
-------  --------------------------------------
   f  g     min
c  5  7  c    1
d  3  6  d    2
>>> mf.call(np.min)
1
>>> mf.log1p()
(3, 2)    g         7         6
          f         5         3
                    c         d
--------  ---------------------
   x  y             c         d
a  1  2   a  0.693147  1.098612
b  3  6   b  2.197225  2.302585
b  5  6   b  2.197225  2.079442
>>> mf.df.log1p()
AttributeError

``pandas.DataFrame.min`` returns the minimum values of each column by default. ``numpy.min`` returns the minimum value of all values by default. The above example shows that ``mf.min`` uses ``pandas.DataFrame.min`` under the hood. 

As explained in :ref:`proper_function`, functions must satisfied certain rules to be used with the :doc:`call method <call_method>`. Users should check numpy API to decide whether a numpy function in the main namespace can be called as a method of MulSeries or MulDataFrame. As a matter of fact, most of the functions do work with the call method.