Call method
=================

MulDataFrame and MulSeries implements a ``.call`` method to apply a function to the values dataframe and the values series, respectively. The return value of the method depends on the return value of the function. If the funciton returns a scalar, the method returns a scalar. If the function returns a series, the method returns a mulseries. If the function returns a dataframe, the method returns a muldataframe. 

>>> mf
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
a  1  2   a  1  2
b  3  6   b  8  9
b  5  6   b  8  7
>>> mf.call(lambda df:df+1)
(3, 2)    g  7   6
          f  5   3
             c   d
--------  ---------
   x  y      c   d
a  1  2   a  2   3
b  3  6   b  9  10
b  5  6   b  9   8
>>> mf.call(lambda df:df.sum(axis=1))
(3,)     Series([], Name: <lambda>, dtype: object)
-------  -------------------------------------------
   x  y     <lambda>
a  1  2  a         3
b  3  6  b        17
b  5  6  b        15
>>> mf.call(lambda df:df.sum().sum())
35

If the function has extra parameters, you can place them after the function argument.

>>> def poly(df,a,b=0):
...     return df.sum(axis=1)*a+b
>>> mf.call(poly,2,b=1)
(3,)     Series([], Name: poly, dtype: object)
-------  ---------------------------------------
   x  y     poly
a  1  2  a     7
b  3  6  b    35
b  5  6  b    31

These examples also illustrate a feature of the method that if the values dataframe is reduced to a series by the function, the function name will be the name of the new series.

.. _proper_function:

Proper function
-----------------
Not all functions applicable to the values dataframe are valid input to the call method. I define a proper function as one that can be used as input to the call method. In general, a proper function is either one that returns a scalar or one that returns a series or a dataframe whose index (and columns) can be matched to that (those) of the values series or dataframe. This requirement is necessary for the call method to properly arrange the index (and columns) dataframes for the return value.

For a mulseries, if the function returns a series, the series must satisfy the following index matching rules:

    - Its shape must be the same as the values series.
    - If the index of the values series has duplicate values, its index must be the same as the index of the values series.
    - If the index of the values series does not have duplicate values, its index can differ from the index of the values series by order and only by order.

>>> ms
(3,)     g  7
         f  5
            c
-------  ------
   x  y     c
a  1  2  a  1
b  3  6  b  8
b  5  6  b  8
>>> def reorder(ss):
...     return ss.iloc[::-1]
>>> ms.call(reorder)
NotImplementedError
>>> ms.iloc[:2].call(reorder)
(2,)     g  7
         f  5
            c
-------  ------
   x  y     c
b  3  6  b  8
a  1  2  a  1


For a muldataframe, if the function returns a dataframe, the dataframe's index and columns must both satisfy the index matching rules as shown above.

For a muldataframe, if the function returns a series, the method will run the following procedures:

    - Match the series' index to the index and the columns of the values dataframe using the index matching rules. If one matches and the other does not match, it will construct a mulseries using the series as the values series and the matched index (or columns) dataframe as the index dataframe. The mulseries will be returned by the call method. 
    - If both match, it will try to find if the function has a ``axis`` keyword argument. If it exists and ``axis=1`` or defaults to 1, it will use the index dataframe as the index dataframe of the mulseries. If it exists and ``axis=0`` or defaults to 0, it will use the columns dataframe as the index dataframe of the mulseries. 
    - If both match and the ``axis`` argument does not exist, the call method raises ``NotImplementedError``.

>>> mf2
(2, 2)    g  7  6
          f  5  3
             a  b
--------  ---------
   x  y      a  b
a  1  2   a  1  2
b  3  6   b  8  9
>>> def sum(df,axis=0):
...   return df.sum(axis=axis)
>>> mf2.call(sum)
(2,)     Series([], Name: sum, dtype: object)
-------  --------------------------------------
   f  g     sum
a  5  7  a    9
b  3  6  b   11
>>> 
>>> mf2.call(sum,axis=1)
(2,)     Series([], Name: sum, dtype: object)
-------  --------------------------------------
   x  y     sum
a  1  2  a    3
b  3  6  b   17
>>> 
>>> def sum2(df):
...   return df.sum()
>>> mf2.call(sum2)
NotImplementedError
