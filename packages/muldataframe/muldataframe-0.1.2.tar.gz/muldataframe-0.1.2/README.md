<!-- # <img src="doc/source/_static/header.png" alt="logo" align='middle' style="width: 300px;max-width: 100%"/> -->
# MulDataFrame
### Towards a more intuitive multi-index data frame

*"A multi-index is just a data frame, period."*

![Architecture](doc/source/_static/figure.png)

Have you found the multi-index in pandas difficult to use? With unexpected behaviors? Do you want to get rid of the long and hard-to-remember methods and objects like get_level_values() and pd.IndexSlicer? Have you wondered why a multi-index is so similar to a data frame but is not one? Have you been confused with the difference between levels and columns?

If you answered yes to any of these questions, then MulDataFrame is right for you. MulDataFrame uses pandas data frames as index and columns, which means you can manipulate them with all the familiar methods of a pandas data frame and no more. 
### Installation
```shell
pip install muldataframe
```

### [Documentation](https://frlender.github.io/muldataframe-doc)
### Introduction

A MulDataFrame object consists of three pandas data frames: an index data frame, a columns data frame and a values data frame. They are accessed through the `.index`, `.columns` and `.df` attributes of the muldataframe. The index of the index data frame and the index of the columns data frame are guaranteed to be the same as the index and the columns of the values data frame. I'll call them the primary index and the primary columns.
```python
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
````

Because of the primary index and columns, you can use `__getitem__`, `iloc` and `loc` on a muldataframe exactly as on its values data frame, except that the return value is a muldataframe (or a mulseries) with its index and columns properly sliced. 

```python
>>> mf.primary_index
Index(['a', 'b', 'b'], dtype='object')
>>> mf.loc['b']
(2, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
b  3  6   b  8  9
b  5  6   b  8  7
>>> mf.loc[mf['d']<9]
(2, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
a  1  2   a  1  2
b  5  6   b  8  7
```
MulDataFrame uses `.mloc` to perform multi-indexing. Its input can be a list or a dict. If a list is used, it has a similar syntax to that of pandas except that you don't need to create a `pd.IndexSlicer` object. Just input a plain list with `...` as placeholders. The example below returns a MulSeries object whose name is a pandas Series and index a pandas data frame.
```python
# the result is a MulSeries object
>>> mf.mloc[[..., 6],[3]]
(2,)     g  6
         f  3
            d
-------  ------
   x  y     d
b  3  6  b  9
b  5  6  b  7
```
MulDataFrame implements a new pattern of multi-indexing called [successive indexing](https://frlender.github.io/muldataframe-doc/user_guide/multi-indexing.html#successive-indexing) rather than [hierarchical indexing](https://pandas.pydata.org/docs/user_guide/advanced.html). You can change the order of successive indexing using a dict indexer.
```python
>>> mf.mloc[{'y':[2,6],'x':[3]}]
(1, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   x  y      c  d
b  3  6   b  8  9
```
In the above example, the muldataframe is first indexed by the `y` column of the index data frame and then the `x` column. With a list as input you cannot achieve this. In fact, `mf.mloc[[[3],[2,6]]]` reports an error. 

`mf.mindex` and `mf.mcolumns`/`mf.mcols` are implemented as alias for `mf.index` and `mf.columns` to help distinguish between a multi-index and a regular index. `mf.pindex` and `mf.pcolumns`/`md.pcols` are implemented as shorthands for `mf.primary_index` and `mf.primary_columns`. We'll use these alias in the following examples.

```python
>>> mf.pcols
Index(['c', 'd'], dtype='object')
>>> mf.mindex
   x  y
a  1  2
b  3  6
b  5  6
```

Because of the locking of the primary index and columns, if you change the index of the index data frame, the index of the values data frame will also change. The same applies to the index of the columns data frame.

```python
>>> mf2 = mf.copy()
# mf2.pindex = ['d','e',5] also works
>>> mf2.mindex.index = ['d','e',5]
>>> mf2.df
	c	d
d	1	2
e	8	9
5	8	7
```

You can also easily change the primary index to another column in the index data frame by calling the `.set_index()` method of the index data frame.

```python
>>> mf2.mindex.set_index('x',inplace=True)
>>> mf2
(3, 2)    g  7  6
          f  5  3
             c  d
--------  ---------
   y         c  d
x         x
1  2      1  1  2
3  6      3  8  9
5  6      5  8  7
```
With the ``MulDataFrame.query`` method, you can query the three data frames alone or in combinations:
```python
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
```
