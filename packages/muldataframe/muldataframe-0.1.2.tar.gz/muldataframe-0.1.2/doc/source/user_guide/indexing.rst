Indexing
==========

.. TODO: loc and iloc as setter

Because of the primary index and columns (see :doc:`Data structures <data_structures>`), you can use ``__getitem__``, ``.iloc`` and ``.loc`` on a muldataframe exactly as on its values dataframe, except that the return value is a muldataframe (or a mulseries) with its index and columns properly sliced. The same mechanism applies to a mulseries. 

>>> mf
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
a  1  2   a  1  2
b  3  6   b  8  9
b  5  6   b  8  7
>>> mf['d']
(3,)      g  6
          f  3
             d
--------  ---------
   x  y      d
b  3  6   b  9
b  5  6   b  7
>>> mf.loc['b']
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
b  3  6   b  8  9
b  5  6   b  8  7
>>> mf.loc['a','c']
1
>>> mf.iloc[[0,1],[0]]
(3, 1)    g  7
          f  5
             c
--------  ---------
   x  y      c
a  1  2   a  1
b  3  6   b  8
>>> mf.iloc[:,0]['b']
(3,)      g  7
          f  5
             c
--------  ---------
   x  y      c
b  3  6   b  8
b  5  6   b  8

The same indexers can also be used to set values:

>>> mf2 = mf.copy()
>>> mf2.loc['a'] = [5,7]
>>> mf2.values
array([[5, 7],
       [8, 9],
       [8, 7]])
>>> mf2['c'] = [8,9,10]
>>> mf2.values
rray([[ 8,  7],
      [ 9,  9],
      [10,  7]])

      