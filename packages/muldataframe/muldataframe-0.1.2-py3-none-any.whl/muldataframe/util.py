import pandas as pd
import muldataframe.cmm as cmm
import muldataframe as md
# import muldataframe.cmm as cmm
# import typing

def aggregate_index(i:int,index:pd.DataFrame,index_agg:cmm.IndexAgg) -> pd.DataFrame:
    # agg_mode: 'same_only', 'array'
    # print(key)
    
    # if isinstance(key,tuple) or \
    #     not isinstance(key,typing.Hashable):
    #     final_index = pd.Index([i])
    # else:
    #     final_index = pd.Index([key])
    final_index = pd.Index([i])
    if index_agg == 'same_only':
        # print(index[index.columns[0]].unique())
        index_same = index.loc[:,[len(index[col].unique())==1 for col in index.columns]]
        index_one = index_same.iloc[[0]]
        index_one.index = final_index
        # print('====',index,'\n',index_same,'\n',index_one)
        return index_one
    elif index_agg in ['list','tuple']:
        index_vals = []
        for col in index.columns:
            vals = index[col].unique()
            if len(vals) == 1:
                index_vals.append(vals[0])
            else:
                vals = tuple(vals) if index_agg == 'tuple' else vals
                index_vals.append(vals)
        return pd.DataFrame([index_vals],columns=index.columns,index=final_index)

        

def concat(arr:list[md.MulSeries|md.MulDataFrame],axis=0):
    '''
    Concatenate muldataframe objects along a particular axis.

    The list of muldataframe objects are joined by the primary index or columns depending on the specified axis. Index or columns dataframes along the axis are concatenated. Index or columns dataframes on the other axis are ignored except for the first one. The first one is used as the index or columns dataframe of the final muldataframe object. Currently, only inner join is supported. 

    Parameters
    -------------
    objs : a list of MulSeries or MulDataFrame objects
        It can be a mix of mulseries and muldataframes.
    axis : {0, 1}, default 0
        The axis to concatenate along.

    Returns
    ----------
    MulSeries or MulDataFrame
        It will return a mulseries only if the objects in the list are all mulseries and are concatenated along ``axis=0``
    
    Examples
    ---------
    >>> import pandas as pd
    >>> import muldataframe as md
    >>> index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','c'],
                     columns=['x','y'])
    >>> columns = pd.DataFrame([[5,7],[3,6]],
                        index=['c','d'],
                        columns=['f','g'])
    >>> mf = md.MulDataFrame([[1,2],[8,9],[8,10]],index=index, columns=columns)
    >>> ms = md.MulSeries([5,6,7],
            index=pd.DataFrame(index=['a','b','c']),
            name=pd.Series([8,9],index=['g','f']))
    >>> pd.concat([mf,ms],axis=1)
    (3, 3)    g  7   6  8
              f  5   3  9
                 c   d  k
    --------  ------------
       x  y      c   d  k
    a  1  2   a  1   2  5
    b  3  6   b  8   9  6
    c  5  6   c  8  10  7
    >>> pd.concat([ms,mf],axis=1)
    (3, 3)            f  9  5   3
                      g  8  7   6
                         k  c   d
    ----------------  ------------
    Empty DataFrame      k  c   d
    Columns: []       a  5  1   2
    Index: [a, b, c]  b  6  8   9
                      c  7  8  10
    '''
    ds_new = pd.concat([x.ds for x in arr],join='inner',axis=axis)
   
    # print('ddddddd',mds1.ds,mds2.ds,ds_new)
    if isinstance(ds_new,pd.Series):
        mindex_new = pd.concat([x.index for x in arr],join='inner')
        return md.MulSeries(ds_new.values,index=mindex_new,
                    name=arr[0].name,index_copy=False)
    else:
        if axis == 0:
            mindex_new = pd.concat([x.index for x in arr],join='inner')
            return md.MulDataFrame(ds_new.values,index=mindex_new,
                    columns=arr[0].columns,index_copy=False)
        else:
            mcols_new = pd.concat([x.columns 
                if isinstance(x,md.MulDataFrame) else pd.DataFrame(x.name).transpose() for x in arr],join='inner')
            # print('***************')
            # print(ds_new)
            # print(mcols_new)
            return md.MulDataFrame(ds_new.values,index=arr[0].index,
                    columns=mcols_new,columns_copy=False)
    

def pivot_table(*args,**kwargs):
    '''
    Same as ``pandas.pivot_table`` except that it returns a MulDataFrame.

    If with the same arguments, ``pandas.pivot_table`` returns a dataframe with no multiindex. Then this function will return a muldataframe with empty index and columns dataframes. 
    
    Check :doc:`MulDataFrame.melt <../muldataframe/melt>` for a reverse operation.

    Parameters
    -----------
    The parameters are exactly the same as in `pandas.pivot_table <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pivot_table.html#pandas.DataFrame.pivot_table>`_. Please check its web page for detailed usage.

    Returns
    --------
    MulDataFrame
        returns a MulDataFrame

    Examples
    ----------
    >>> import pandas as pd
    >>> import muldataframe as md
    >>> df = pd.DataFrame({"A": ["foo", "foo", "foo", "foo", "foo",
                         "bar", "bar", "bar", "bar"],
                   "B": ["one", "one", "one", "two", "two",
                         "one", "one", "two", "two"],
                   "C": ["small", "large", "large", "small",
                         "small", "large", "small", "small",
                         "large"],
                   "D": [1, 2, 2, 3, 3, 4, 5, 6, 7],
                   "E": [2, 4, 5, 5, 6, 6, 8, 9, 9]})
    >>> md.pivot_table(df, values='D', index=['A', 'B'], columns=['C'], aggfunc="sum")
    (4, 2)       Empty DataFrame
                 Columns: []
                 Index: [large, small]
    -----------  -----------------------
        A    B   C  large  small
    0  bar  one  0    4.0    5.0
    1  bar  two  1    7.0    6.0
    2  foo  one  2    4.0    1.0
    3  foo  two  3    NaN    6.0
    '''
    df = pd.pivot_table(*args,**kwargs)
    # print(df)
    if isinstance(df.index,pd.MultiIndex):
        new_idx = df.index.to_frame(index=False)
    else:
        new_idx = pd.DataFrame(index=df.index)
    if isinstance(df.columns,pd.MultiIndex):
        new_cols = df.columns.to_frame(index=False)
    else:
        new_cols = pd.DataFrame(index=df.columns)
    
    return md.MulDataFrame(df.values,
                           index=new_idx,
                           columns=new_cols,
                           both_copy=False)