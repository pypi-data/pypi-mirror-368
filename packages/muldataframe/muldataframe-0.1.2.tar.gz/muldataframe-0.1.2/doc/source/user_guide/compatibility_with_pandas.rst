Operators and compatibility
==============================
Operators can be used with MulDataFrame and MulSeries. 

>>> mf
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
a  1  2   a  1  2
b  3  6   b  8  9
b  5  6   b  8  7
>>> mf-1
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
a  1  2   a  0  1
b  3  6   b  7  8
b  5  6   b  7  6
>>> (mf**2).iloc[1,0]
64

Except for the ``=`` operator, all operators are implemented using the :doc:`call_method` with the special operator methods of the values series or dataframe as the input (see :doc:`pandas_methods`). For example, the ``+`` operator is implemented as:

>>> class MulDataFrame:
    ...
    def __add__(self,other):
        return self.call('__add__',other)
    ...

The ``=`` operator is implemented using the ``.equals`` method as input. 

Because of the use of the call method, an operation is only valid if:

    - the operation is a valid operation on the underlying values series or dataframe(s).
    - the result of the operation on the values series or dataframe(s) satisfies the :ref:`index matching rules <proper_function>`.

For example, the ``+`` operation below works on the values dataframes of the two muldataframes but does not work on the muldataframes themselves:

>>> mf2
(2, 2)    f  5  3
             c  d
--------  ---------
   y         c  d
a  2      a  1  2
b  6      b  8  9
>>> mf3
(2, 2)    f  5  3
             c  d
--------  ---------
   y         c  d
a  2      a  1  2
c  6      c  8  9
>>> mf2.df + mf3.df
	c	d
a	2.0	4.0
b	NaN	NaN
c	NaN	NaN
>>> mf2 + mf3
NotImplementedError

Also becuase of the call method, when two muldataframes are operated, the result inherits the index or/and columns of the first muldataframe and ignore the index and columns of the second.

>>> mf+mf2
(3, 2)    g   7   6
          f   5   3
              c   d
--------  ---------
   x  y       c   d
a  1  2   a   2   4
b  3  6   b  16  18
b  5  6   b  16  16
>>> mf2+mf
NotImplementedError

Of note, the ``mf2+mf`` in the above example does not work because the addition result of the values dataframes does not satisfy the index mathcing rules of ``mf2`` while it does satisfy the rules of ``mf``.

Compatibility with pandas
----------------------------
As all operators (except for ``=``) are implemented using the :doc:`call_method`, they can be used between a pandas object and a MulDataFrame object. The order in which a pandas object and a MulDataFrame object are operated on does not matter!

>>> mf2 / mf2.df
(2, 2)    f   5     3
              c     d
--------  -----------
   y           c    d
a  2      a  1.0  1.0
b  6      b  1.0  1.0
>>> mf2.df / mf2
(2, 2)    f    5    3
               c    d
--------  -----------
   y           c    d
a  2      a  1.0  1.0
b  6      b  1.0  1.0



