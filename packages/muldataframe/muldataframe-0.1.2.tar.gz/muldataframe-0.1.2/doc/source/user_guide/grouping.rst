Grouping
=========

A muldataframe can be grouped by column(s) in its index or columns data frame but not its values data frame using the ``groupby`` method. The method uses the `pandas.DataFrame.groupby <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html#pandas.DataFrame.groupby>`_ method of the index or columns dataframe to create groups under the hood. The values data frame is grouped accordingly. It returns a ``MulGroupBy`` object that contains information about the groups. It can be similarly iterated as its counterpart in pandas:

>>> mf
(3, 2)    g  7   6
          f  5   3
             c   d
--------  ---------
   x  y      c   d
a  1  2   a  1   2
b  3  6   b  8   9
b  5  6   b  8  10
>>> for key, group in mf.groupby('y'):
...     if key == 6:
...         print(key,'\n',group)
6
(2, 2)    g  7   6
          f  5   3
             c   d
--------  ---------
   x  y      c   d
b  3  6   b  8   9
b  5  6   b  8  10

The ``MulGroupBy`` class implements a similar ``call`` method as that of the ``MulDataFrame`` class and has all the numpy functions added to it through the method. The method applies an input function to the values data frame in each group and concateate the return values into a final muldataframe. You can thus call numpy functions after the ``groupby`` method to compute group statistics.

>>> mf.groupby('y').mean()
(2, 2)           g    7    6
                 f    5    3
                      c    d
---------------  -----------
Empty DataFrame       c    d
Columns: []      y
Index: [2, 6]    2  1.0  2.0
                 6  8.0  9.5

By default, the primary index is dropped and only columns with identical values in each group are kept in the result of the ``call`` method. You can change this behavior by specifying the ``agg_mode`` and ``keep_primary`` arguments. 

>>> mf.groupby('y',agg_mode='list',keep_primary=True).mean()
(2, 2)                   g    7    6
                         f    5    3
                              c    d
-----------------------  -----------
  primary_index       x       c    d
y                        y
2             a       1  2  1.0  2.0
6             b  [3, 5]  6  8.0  9.5

When a muldataframe is grouped by a single column, the values in that column will become the primary index or column of the muldataframe returned by the ``call`` method. If it is grouped by multiple columns, the primary index will be a range of integers.

>>> mf.index.iloc[2] = [3,6]
>>> mf.groupby(['x','y']).mean()
(2, 2)    g    7    6
          f    5    3
               c    d
--------  -----------
   x  y        c    d
0  1  2   0  1.0  2.0
1  3  6   1  8.0  8.0

The ``groupby`` method does not directly support grouping by the values data frame because it normally stores numeric data while the index and columns data frames store metadata. It is by metadata that grouping mostly occurs. A similar ``groupby`` method is implemented for the index data frame of the ``MulSeries`` class. 