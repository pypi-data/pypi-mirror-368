Data Structures
==================

MulDataFrame
--------------

A MulDataFrame object consists of three pandas dataframes: an index dataframe, a columns dataframe and a values dataframe. They are accessed through the ``.index``, ``.columns`` and ``.df`` attributes of the muldataframe. While ``.index`` and ``.columns`` refer to the index and the columns dataframes, ``.df`` provides a deepcopy of the values dataframe.

>>> import pandas as pd
>>> import muldataframe as md
>>> index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
>>> columns = pd.DataFrame([[5,7],[3,6]],
                    index=['c','d'],
                    columns=['f','g'])
>>> mf = MulDataFrame([[1,2],[8,9],[8,7]],
    index=index,columns=columns)
>>> mf
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
a  1  2   a  1  2
b  3  6   b  8  9
b  5  6   b  8  7
>>> mf.columns
   f  g
c  5  7
d  3  6
>>> mf.df
   c  d
a  1  2
b  8  9
b  8  7

``.ds`` provides a paritial copy of the values dataframe. Its values are not copied but refer to the values of the values dataframe while its index and columns are deep-copied from the values dataframe. The ``.values`` attribute of a muldataframe refers to the values of the values dataframe. 

>>> mf2 = mf.copy()
>>> mf2.values[0,1] = 5
>>> mf2.ds
   c  d
a  5  2
b  8  9
b  8  7

The index of the index dataframe and the index of the columns dataframe are guaranteed to be the same as the index and the columns of the values dataframe. They are called the primary index and the primary columns. The ``.primary_index`` attribute refers to the index of the index dataframe. The ``.primary_columns`` refers to the index of the columns dataframe.

>>> mf2 = mf.copy()
>>> mf2.index.index = ['d','e',5]
>>> mf2.df
   c  d
d  1  2
e  8  9
5  8  7
>>> mf2.primary_index
['d','e',5]
>>> mf2.primary_columns
['c','d']


``.mindex`` and ``.mcolumns/mf.mcols`` are implemented as alias for ``.index`` and ``.columns`` to help distinguish between a multi-index and a regular index. ``.pindex`` and ``.pcolumns/md.pcols`` are implemented as shorthands for ``.primary_index`` and ``.primary_columns``. The shape of a muldataframe is the same as the shape of its underlying values dataframe

>>> mf.pcols
Index(['c', 'd'], dtype='object')
>>> mf.mindex
   x  y
a  1  2
b  3  6
b  5  6
>>> mf.shape
(3,2)

MulSeries
-----------
A MulSeries object consists of one pandas dataframe and two pandas series: an index dataframe, a name series and a values series. They are accessed through the ``.index``, ``.name`` and ``.ss`` attributes of the mulseries. While ``.index`` and ``.name`` refer to the index dataframe and the name series, ``.ss`` provides a deepcopy of the values series.

>>> import pandas as pd
>>> import muldataframe as md
>>> index = pd.DataFrame([[1,2],[3,5],[3,6]],
                        index=['a','b','b'],
                        columns=['x','y'])
>>> name = pd.Series(['g','h'],index=['e','f'], name='cc')
>>> ms = md.MulSeries([1,2,3],index=index,name=name)
>>> ms
(3,)     f   h
         e   g
            cc
-------  ------
   x  y     cc
a  1  2  a   1
b  3  5  b   2
b  3  6  b   3
>>> ms.ss
   cc
a   1
b   2
b   3

Similar to MulDataFrame, ``.ds`` provides a paritial copy of the values series. Its values are not copied but refer to the values of the values series while its index and name are deep-copied from the values series. The ``.values`` attribute of a mulseries refers to the values of the values series. 

Similar to MulDataFrame, the index of the index dataframe and the name of the name series are guaranteed to be the same as the index and the name of the values series. They are called the primary index and the primary name. The ``.primary_index`` attribute refers to the index of the index dataframe. The ``.primary_name`` refers to the name of the name series.

``.mindex`` and ``.mname`` are implemented as alias for ``.index`` and ``.name`` to help distinguish between a multi-index and a regular index. ``.pindex`` and ``.pname`` are implemented as shorthands for ``mf.primary_index`` and ``primary_name``. The shape of a mulseries is the same as the shape of its underlying values series