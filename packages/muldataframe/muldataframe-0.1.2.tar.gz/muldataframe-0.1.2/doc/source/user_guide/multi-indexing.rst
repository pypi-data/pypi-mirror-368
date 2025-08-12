Multi-indexing
================

.. mloc as setter

mloc
-----
MulDataFrame uses ``.mloc`` to perform multi-indexing. It implements a different multi-indexing pattern from that of pandas. pandas implements hierarchical indexing while MulDataFrame implements what we call *successive indexing*. Their difference is discussed later on this page. The input to ``.mloc`` can be a list or a dict. If a list is used, it has a similar syntax as that in pandas except that you don't need to create a ``pandas.IndexSlicer`` object. Just input a plain list with ``...`` as placeholders to select all values in a column.

>>> mf
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
a  1  2   a  1  2
b  3  6   b  8  9
b  5  6   b  8  7
>>> mf.mloc[[..., 6],[3]]
(2,)     g  6
         f  3
            d
-------  ------
   x  y     d
b  3  6  b  9
b  5  6  b  7

The above example uses the "y" column in the index dataframe to select the 2nd and 3rd rows and the "f" columns in the columns dataframe to select the 2nd column.

As the column selection is a scalar selection, the return value is a mulseries rather than a muldataframe. The hierachical indexing in pandas implements a different behavior that a scalar selection in a data frame on a single level still results in a data frame. Only when selections on *all* levels are scalar selections does hierachical indexing result in a series. In successive indexing, a scalar selection on *any* level results in a mulseries. We believe our implementation is a more intuitive choice as it is what is expected from a single index. Of note, a scalar label does not always lead to a scalar selection as the label might be duplicated.

.. _successive_indexing:

The reason successive indexing is named as such is illustrated by the following example:

>>> mf.mloc[[[1,3], 6]]
(2,)     y  6
         x  3
            b
-------  ------
   f  g     b
c  5  7  c  8
d  3  6  d  9 
>>> mf2 = mf.mloc[[[1,3]]]
>>> mf2.mloc[[..., 6]]
(2,)     y  6
         x  3
            b
-------  ------
   f  g     b
c  5  7  c  8
d  3  6  d  9

So a multi-indexing operation on a muldataframe is the same as successively applying the indexer in each column of the index data frame to the muldataframe. It adheres to the idea that a multi-index is just a collection of single indexes. Hierarchical indexing in pandas, on the other hand, is more like selecting the intersection of the different levels' indexers. Their difference is illustrated by the following example:

>>> mf.mloc[[[3], [2,6]]]
Error
>>> df = mf.df
>>> df.index = pd.MultiIndex.from_frame(mf.index)
>>> df
     c  d
x y      
1 2  1  2
3 6  8  9
5 6  8  7
>>> ix = pd.IndexSlice
>>> df.loc[ix[[3],[2,6]],:]
     c  d
x y      
3 6  8  9

An intricacy to notice is that ``mf.mloc[[3,[2,6]]]`` does not report an error and returns the second row as a mulseries. This is because successive indexing is implemented as such that when a scalar selection is reached in the middle of a multi-indexing, the following indexers only need to include this selection to be valid. The example also shows you must fill in ``:`` as the column indexer in hierachical indexing even if you only need to index rows. 

With a dict as input, you can change the order of successive indexing and fix the error in the above example:

>>> mf.mloc[{'y':[2,6],'x':[3]}]
(1, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
b  3  6   b  8  9
```

In this example, the muldataframe is first indexed by the "y" column and then the "x" column of the index data frame.  

When there are duplicate names in the columns of the index or columns dataframe, use the **last** column for dict indexing.

>>> mf2
(3, 2)      g  7  6
            f  5  3
               c  d
----------  ---------
   x  y  y     c  d
a  1  2  8  a  1  2
b  3  6  5  b  8  9
b  5  6  2  b  8  7
>>> mf2.mloc[{'y':[2]}]
(1, 2)      g  7  6
            f  5  3
               c  d
----------  ---------
   x  y  y     c  d
b  5  6  2  b  8  7


Users can mixedly use the two types of indexers in a muldataframe with, for exmaple, a dict indexer for the rows and a list indexer for the columns.

>>> mf.mloc[{'y':[2,6],'x':[3]},[..., 7]]
(1,)      g  7
          f  5
             c
--------  ---------
   x  y      c
b  3  6   b  8

``.mloc`` is also implemented for MulSeries:

>>> ms = mf['c']
>>> ms.mloc[[..., 6]]
(2,)     g  7
         f  5
            c
-------  ------
   x  y     c
b  3  6  b  8
b  5  6  b  8

You can also use ``.mloc`` to set values:

>>> mf3 = mf.copy()
>>> mf3.mloc[{'x':3},{'f':5}] = 7 
>>> mf3.df
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
a  1  2   a  1  2
b  3  6   b  0  9
b  5  6   b  8  7
>>> mf3.mloc[[..., 2]] = [3,5]
>>> mf3.df
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
a  1  2   a  3  5
b  3  6   b  0  9
b  5  6   b  8  7

nloc
-------

MulDataFrame and MulSeries also implements ``.nloc`` to enable position-based multi-indexing. If a list is used as input, it behaves exactly the same as ``.mloc``.  If a dict is used, it behaves similarly to ``.mloc`` except that instead of using column names as keys, it uses the numeric positions of the columns as keys.

>>> mf2.nloc[{1:6}]
(2, 2)      g  7  6
            f  5  3
               c  d
----------  ---------
   x  y  y     c  d
b  3  6  5  b  8  9
b  5  6  2  b  8  7

Note that with a dict as input to ``.mloc``, you can only select the last "y" column in the index dataframe. Using ``.nloc`` you can select the first "y" column.

``.nloc`` can also be used to set values.


.. Difference to pandas
.. ----------------------
.. The multi-indexing in MulDataFrame is implemented differently to that in pandas (version 2.2.0) in two cases. First, when a pandas dataframe is multi-indexed on the row dimension, ``:`` must be filled in as the column indexer. Otherwise, an error occurred.

.. >>> df
..        c  d
.. x  y		
.. 1  2   1  2
.. 3  6   8  9
.. 5  6   8  7
.. >>> idx = pd.IndexSlicer
.. >>> df.loc[idx[:,6],:]
..        c  d
.. x  y		
.. 3  6   8  9
.. 5  6   8  7
.. >>> df.loc[idx[:,6]]
.. Error

.. The MulDataFrame's multi-indexing has no such problem as shown by the ``.mloc`` examples above. 

.. Second, in pandas multi-indexing, a scalar selection does not reduce a dataframe to a series or a series to a scalar. In contrast, a scalar selection in MulDataFrame always reduces a muldataframe's or a mulseries' dimension.

.. >>> df.loc[idx[:,2],:]
..       c  d
.. x  y		
.. 1  2  1  2
.. >>> df.loc[idx[:,2],:].shape
.. (1, 2)
.. >>> mf
.. (3, 2)    g  7  6
..           f  5  3
..              c  d
.. --------  ---------
..    x  y      c  d
.. a  1  2   a  1  2
.. b  3  6   b  8  9
.. b  5  6   b  8  7
.. >>> mf.mloc[[..., 2]]
.. (2,)     y  2
..          x  1
..             a
.. -------  ------
..    f  g     a
.. c  5  7  c  1
.. d  3  6  d  2
