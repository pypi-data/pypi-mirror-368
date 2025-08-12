Initialization
===============



MulDataFrame
--------------
The basic constructor signature is:

.. code-block:: python
    
    class muldataframe.MulDataFrame(data, index=None, columns=None, 
        index_init=None, columns_init=None, ...)

The input to the ``index`` and ``columns`` arguments must be pandas DataFrames. The input to the ``data`` argument should follow the same rules as required by the ``data`` argument in the `pandas.DataFrame <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html#pandas.DataFrame>`_ constructor. The values dataframe is constructed from the ``data`` argument.

If the ``index`` or ``columns`` argument is ``None``, an empty index or columns dataframe is created with its index being the same as the index or columns of the values dataframe. If they are not ``None``, the final values dataframe is constructed in either of two modes as specified by the ``index_init`` and the ``columns_init`` arguments.

Overide mode
^^^^^^^^^^^^^^
If ``index_init="override"``, the index of the index dataframe overrides the index of the values dataframe. This mode requires both indices' lengths to be the same. Similarly, if ``columns_init="override"``, the index of the columns dataframe overrides the columns of the values dataframe. The two indices' lengths should also be the same.

>>> import pandas as pd
>>> import muldataframe as md
>>> index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
>>> columns = pd.DataFrame([[5,7],[3,6]],
                    index=['c','d'],
                    columns=['f','g'])
>>> df = pd.DataFrame([[1,2],[8,9],[8,7]],index=['k','l','m'],columns=['t',5])
>>> mf = md.MulDataFrame(df, index=index,
    columns=columns, index_init='override',
    columns_init='override')
>>> mf
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
a  1  2   a  1  2
b  3  6   b  8  9
b  5  6   b  8  7


Align mode
^^^^^^^^^^^^
If ``index_init="align"``, the index of the index dataframe is used to index the values dataframe constructed from the ``data`` argument. The resulting indexed values dataframe is used as the final values dataframe. It requires the index of the values dataframe to be uinque and contain all the labels of the index dataframe's index. If ``columns_init="align"``, the values dataframe is simiarly indexed on the columns dimension by the index of the columns dataframe.

>>> df = pd.DataFrame([[1,2],[8,9]],index=['a','b'],columns=['d','c'])
>>> mf2 = md.MulDataFrame(df, index=index,
    columns=columns, index_init='align',
    columns_init='align')
>>> mf2
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
a  1  2   a  2  1
b  3  6   b  9  8
b  5  6   b  9  8

Default behavior
^^^^^^^^^^^^^^^^^
If ``index_init`` or ``columns_init`` is ``None``, the default behavior depends on the type of the ``data`` argument. Basically, if the ``data`` argument implies an index on a dimension, the align mode will be used for that diemnsion. Otherwise, the override mode is used.

Concretely, with ``index_init=None``, the initialization mode on the row dimension will be ``'align'`` if ``data`` is a ``pandas.DataFrame`` or a ``pandas.Series`` object. With ``columns_init=None``, the initialization mode on the columns dimension will be ``'align'`` if ``data`` is a ``pandas.DataFrame``, a dict of list-like objects or a list of dict objects.

MulSeries
------------

The basic constructor signature is:

.. code-block:: python
    
    class muldataframe.MulSeries(data, index=None, name=None, index_init=None, ...)

The ``index_init`` argument behaves the same as that in the MulDataFrame constructor.

Name initialization
^^^^^^^^^^^^^^^^^^^^^^
The ``name`` argument can be a string or a ``pandas.Series`` object. If ``name`` is a string, construct an empty name series using the ``name`` argument as its name. If ``name`` is ``None``, construct an empty name series using the name of the values series as its name.


