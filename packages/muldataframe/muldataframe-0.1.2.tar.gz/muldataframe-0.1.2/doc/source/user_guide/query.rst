Query
======

With the ``MulDataFrame.query`` method, you can query the index, columns and values dataframes alone or in combinations:

>>> mf
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
a  1  2   a  1  2
b  3  6   b  8  9
b  5  6   b  8  7
>>> mf.query('d < 9',index='y==6')
(1, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
b  5  6   b  8  7
>>> mf.query('d < 9',index='y==6',columns='f==5')
(1, 1)    g  7
          f  5
             c
--------  ------
   x  y      c
b  5  6   b  8
>>> mf.query(index='y==6')
(2, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
b  3  6   b  8  9
b  5  6   b  8  7