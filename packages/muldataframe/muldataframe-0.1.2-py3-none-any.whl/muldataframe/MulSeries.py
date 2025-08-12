import pandas as pd
import muldataframe.cmm as cmm
# import muldataframe.util as util
from typing import Any
import numpy as np
import muldataframe as md
# import muldataframe.ValFrameBase as vfb
import muldataframe.ValFrameBase as vfb
import tabulate
tabulate.PRESERVE_WHITESPACE = True

# import collections.abc

#TODO: query for mulseries and muldataframe

class MulSeries:
    '''
    A multi-index series with the index being a pandas dataframe and the name a pandas series. It also has an underlying values series that is not directly accessible. Its values are the same as the values of the values series.

    Parameters
    -----------
    data: pandas.Series, array-like, Iterable, dict, or scalar value
        either a pandas Series or the same kind of data argument as required in the `pandas Series constructor <https://pandas.pydata.org/docs/reference/api/pandas.Series.html#pandas.Series>`_. The values series is constructed from the data argument.
    index: pandas.DataFrame
        If index is None, construct an empty index dataframe using the index of the values series as its index.
    name: pandas.Series, str
        If name is of str type, construct an empty name series using name as its name. If name is None, construct an empty name series using the name of the values series as its name.
    index_init: Literal['override'] | Literal['align']
        The option determins how to align the index of the index dataframe to the index of the values series. 
        
        - 'override' : the index of the index dataframe overrides the index of the values series. This mode requires both indexes' lengths to be the same. 
        - 'align' : This mode is only effective if the data argumnet implies an index and the index argument is not None. In this mode, the index of the index dataframe is used to index the values series constructed from the data argument. The resulting series is used as the final values series. It requires the index of the values series being uinque and have all the labels in the index dataframe's index. 
        - 'overlap' : The overlap of the index of the index dataframe and the index of the values series is used to index the values series and the index dataframe. This mode requires both indexes being unique. 
        - 'None' : the default behavior depends on the type of the ``data`` argument. If ``data`` is a ``pandas.Series`` or a dict, the mode will be ``'overlap```. Otherwise, it will be ``'override'``.
        
        Of note, when the data arugment is a series or a dict with its index being the same as the index of the index dataframe, neither of the 'align' or 'overlap' mode will be used even if they are specified. As a result, both indexes can have duplicate values.
    index_copy: bool
        whether to create a copy of the index argument.
    name_copy: bool
        whether to create a copy of the name argument.
    data_copy : bool, default None
        Wether to copy ``data``. It behaves the same as the ``copy`` argument in `pandas.Series.__init__ <https://pandas.pydata.org/docs/reference/api/pandas.Series.html>`_

    Examples:
    ----------
    Construct a mulseries. Notice that the index of the dataframe and the index of the values series are the same and the name of the name series and the name of the values series are the same.
    
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
    '''
    # force pandas to return NotImplemented when using ops like +, * 
    # in the case of pd.Series + MulSeries.
    __pandas_priority__ = 10000
    def __init__(self,data,index:pd.DataFrame=None,
                 name:pd.Series|str|None=None,
                 index_init:cmm.IndexInit=None,
                 index_copy=True,name_copy=True,
                 data_copy=None):
       
        ss = data
        
        if isinstance(ss,dict):
            ss = pd.Series(ss,copy=data_copy)

        if isinstance(ss,pd.Series):
            index_init = 'overlap' if index_init is None else index_init
            if data_copy:
                ss = ss.copy()
        else:
            index_init = 'override' if index_init is None else index_init
            ss = pd.Series(ss,copy=data_copy)

        if not isinstance(name,pd.Series):
            if isinstance(name,str):
                name = pd.Series([],name=name)
            else:
                name = pd.Series([],name=ss.name)
        else:
            name = name.copy() if name_copy else name

        ss, index = cmm.setMulIndex(ss,'index',index,index_init,index_copy)

        
        self.index = index
        '''
        The index dataframe. 

        Use :doc:`MulSeries.mindex <mindex>` as an alias for this attribute.
        '''
        self.name = name
        '''
        The name series. 

        Use :doc:`MulSeries.mname <mname>` as an alias for this attribute.
        '''
        # print(hasattr(self, 'index'))
        self.__ss = ValSeries(self,ss) # private

        self.iloc = cmm.Accessor(self._xloc_get_factory('iloc'),
                             self._xloc_set_factory('iloc'))
        '''
        Position-based indexing. 

        It is the same as the `Series.iloc <https://pandas.pydata.org/docs/reference/api/pandas.Series.iloc.html>`_ of the values series except that it returns a MulSeries with the index dataframe properly sliced. If the return value is a scalar, it returns the scalar.
        '''
        self.loc = cmm.Accessor(self._xloc_get_factory('loc'),
                            self._xloc_set_factory('loc'))
        '''
        Label-based indexing. 
        
        It is the same as `Series.loc <https://pandas.pydata.org/docs/reference/api/pandas.Series.loc.html>`_ of the values series except that it returns a MulSeries with the index dataframe properly sliced. If the return value is a scalar, it returns the scalar.
        '''
        self.mloc = cmm.Accessor(self._mloc_get,
                             self._mloc_set)
        '''
        Flexible hierachical indexing on the index dataframe. 
        
        The slicer can be a list or a dict. Check introduction to mloc ??? for detailed usage. 
        
        If a list is used, its length should be less than or equal to the columns length of the index dataframe. The hierarchical indexing order is from the leftmost column to the rightmost. Use ``...`` as ``:`` in the list to select all elements in a column.

        If a dict is used, its keys should be the column names of the index dataframe and its values the slicers on the columns. The hierachical indexing order is the insertion order of the keys in the dict. Although Python does not guanrantee the insertion order, it is preserved in most cases. Use the `OrderedDict <https://docs.python.org/3/library/collections.html#collections.OrderedDict>`_ class if you are really concerned about it.

        Examples
        ---------
        List indexing:

        >>> import pandas as pd
        >>> import muldataframe as md
        >>> index = pd.DataFrame([['a','b','c'],
                                  [ 'g','b','f'],
                                  [ 'b','g','h']],
                           columns=['x','y','y'])
        >>> name = pd.Series(['a','b'],index=['e','f'],name='cc')
        >>> ms = md.MulSeries([1,2,3],index=index,name=name)
        >>> ms.mloc[[..., 'b']]
        (2,)        e   a
                    f   b
                       cc
        ----------  ------
           x  y  y     cc
        0  a  b  c  0   1
        1  g  b  f  1   2
        >>> ms.mloc[['g', ..., ['h','f']]]
        2

        Dictionary indexing:

        >>> ms.mloc[{'y':['c','h'],'x':['b','a']}]
        (2,)        e   a
                    f   b
                       cc
        ----------  ------
           x  y  y     cc
        2  b  g  h  2   3
        0  a  b  c  0   1

        Note in the above example that if the index dataframe's columns have duplicate names, use the **last** column for dict indexing.
        
        '''
        self.nloc = cmm.Accessor(self._nloc_get,
                             self._nloc_set)
        '''
        Flexible hierachical indexing on the index dataframe using positions. 
        
        The slicer can be a list or a dict. Check introduction to mloc ??? for detailed usage. 
        
        If a list is used, it behaves exactly like :doc:`mloc`.

        If a dict is used, it behaves similarly to :doc:`mloc` except that instead of using column names as keys, it uses the numeric positions of the columns as keys.

        Examples
        ---------
        Dictionary indexing:

        >>> import pandas as pd
        >>> import muldataframe as md
        >>> index = pd.DataFrame([['a','b','c'],
                                  [ 'g','b','f'],
                                  [ 'b','g','h']],
                           columns=['x','y','y'])
        >>> name = pd.Series(['a','b'],index=['e','f'],name='cc')
        >>> ms = md.MulSeries([1,2,3],index=index,name=name)
        >>> ms.nloc[{1:['b','g'],0:['b','a']}]
        (2,)        e   a
                    f   b
                       cc
        ----------  ------
           x  y  y     cc
        2  b  g  h  2   3
        0  a  b  c  0   1

        Note that with a dict in :doc:`mloc`, you can only select the last ``y`` column in the index dataframe. Using ``nloc`` you are able to select the first ``y`` column.
        '''

    def __repr__(self):
        cols = cmm.fmtSeries(self.name)
        vals = cmm.fmtSeries(self.ds)
        return tabulate.tabulate(
                [[str(self.index),str(vals)]],
               headers=[self.shape,
                        cmm.fmtColStr(cols,False)])
        # return 'ss:\n'+self.__ss.__repr__()+'\n\nindex:\n'+\
        #         self.index.__repr__()+'\n\nname:\n'+\
        #         self.name.__repr__()
    
    def __getattr__(self,name):
        if name == 'values':
            return self.__ss.values
        elif name == 'ss':
            return pd.Series(self.values.copy(),
                             index=self.index.index.copy(),
                             name=self.name.name)
        elif name in ['mindex','mname']:
            return getattr(self,name.lstrip('m'))
        elif name == 'midx':
            return self.index
        elif name in ['primary_index','pindex','pidx']:
            return self.index.index
        elif name in ['primary_name','pname']:
            return self.name.name
        elif name == 'shape':
            return self.__ss.shape
        elif name == 'ds':
            # values are not copied version
            return pd.Series(self.values,
                             index=self.index.index.copy(),
                             name=self.name.name,
                             copy=False)
        elif cmm.is_pandas_method(self,name):
            def func(*args,**kwargs):
                return self.call(name,*args,**kwargs)
            return func
        elif cmm.is_numpy_function(name):
            def func(*args,**kwargs):
                return self.call(getattr(np,name),*args,**kwargs)
            return func

        
    def _hasVal(self):
        return self.__ss is not None

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ['ss','ds']:
            raise AttributeError(f"ss is a read-only attribute.")
        elif name in ['index','mindex','midx']:
            cmm.checkSetIdxValue(self,'index',value)
            super().__setattr__('index', value)
        elif name in ['manme']:
            super().__setattr__('name', value)
        elif name in ['primary_index','pindex','pidx']:
            self.index.index = value
        elif name in ['primary_name','pname']:
            self.name.name = value
        else:
            super().__setattr__(name, value)

    def __len__(self):
        return self.shape[0]
    
    def insert(self,label,value,loc=None,name=None,inplace=True):
        '''
        Insert a value into MulSeries at specified location.

        Duplicate labels are allowed. It is an append operation if ``loc=None``.

        Parameters
        ------------
        label : str, number, or hashable object
            Label of the inserted value
        value : Scalar
            The inserted value.
        loc : int
            Insertion index. Must verify 0 <= loc <= MulSeries.shape[0] if ``axis==0``. If ``loc=None``, insert at the end of the MulSeries, namely an append operation.
        name : Scalar, Series, or array-like
            The metadata of ``value`` inserted into the index dataframe.
        inplace : bool, default True
            Whether insert inplace or return a new MulSeries.

        Returns
        ---------
        None or MulSeries
            returns ``None`` if ``inplace=True``
        
        Examples
        ---------
        >>> import pandas as pd
        >>> import muldataframe as md
        >>> index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
        >>> columns = pd.DataFrame([[5,7],[3,6]],
                        index=['c','d'],
                        columns=['f','g'])
        >>> ms = MulSeries([1,8,9],index=index,name=columns.loc['c'])
        >>> ms.insert('e',7,loc=1,name=[8,9],inplace=False)
        (4,)     g  7
                 f  5
                    c
        -------  ------
           x  y     c
        a  1  2  a  1
        e  8  9  e  7
        b  3  6  b  8
        b  5  6  b  9
        '''
        loc = self.shape[0] if loc is None else loc
        if inplace:
            # self.__ss._update_super_index()
            ds = self.ds
            self.__ss = None
            dsf = pd.DataFrame(ds,copy=False).transpose()
            dsf.insert(loc,label,value)
            
            mindext = self.mindex.transpose()
            if name is None:
                name = [None]*self.mindex.shape[1]
            mindext.insert(loc,label,name)
            self.mindex = mindext.transpose()
            # print('\t',mindext)
            # print('\t',self.index)

            self.__ss = dsf.iloc[0]
        else:
            ms = self.copy()
            ms.insert(label,value,loc,name,True)
            return ms

    
    def drop(self,labels,mloc=None,inplace=False):
        '''
        Remove values from MulSeres by labels.

        Parameters
        ------------
        labels : single label or list-like
            primary index labels if ``mloc=None`` or labels in a column of the index dataframe specified by ``mloc``.
        mloc : None, str, number, or hashable object
            Column name in the index dataframe. if ``mloc=None``, use the primary index to select removed values. Otherwise, use the labels in the specified column to select removed values.
        inplace : bool, default False
            Whether to modify the MulSeries inplace or return a new MulSeries with values removed.
        
        Returns
        --------
        MulSeries or None
            returns ``None`` if ``inplace=True``.
        
        Examples
        -----------
        >>> import pandas as pd
        >>> import muldataframe as md
        >>> index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
        >>> columns = pd.DataFrame([[5,7],[3,6]],
                        index=['c','d'],
                        columns=['f','g'])
        >>> ms = MulSeries([1,8,9],index=index,name=columns.loc['c'])
        >>> ms.drop('b')
        (1,)     g  7
                 f  5
                    c
        -------  ------
           x  y     c
        a  1  2  a  1
        >>> ms.drop(6,mloc='y')
        (1,)     g  7
                 f  5
                    c
        -------  ------
           x  y     c
        a  1  2  a  1
        '''
        if inplace:
            self.__ss._update_super_index()
            __ss = self.__ss
            self.__ss = None
            if mloc is None:
                __ss.drop(labels,inplace=True)
                self.mindex.drop(labels,inplace=True)
            else:
                __ss.index = self.mindex[mloc]
                self.mindex['_&%@x'] = self.mindex.index
                self.mindex.index = self.mindex[mloc]
                self.mindex.drop(labels,inplace=True)
                self.mindex.index = self.mindex['_&%@x']
                self.mindex.drop('_&%@x',inplace=True,axis=1)
                __ss.drop(labels,inplace=True)
                __ss.index = self.mindex.index
            self.__ss = __ss
        else:
            ms = self.copy()
            ms.drop(labels,mloc,inplace=True)
            return ms

   
    def equals(self,other):
        '''
        Test whether two MulSeries are the same.

        Two MulSeries are equal only if their index dataframes, name series and value dataframes are equal. Use `Series.equals <https://pandas.pydata.org/docs/reference/api/pandas.Series.equals.html>`_ and `DataFrame.equals <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.equals.html#>`_ under the hood.

        Parameters
        ------------
        other : object
            The other object to be compared with the MulSeries. If the other is not a MulSeries, returns False.

        Returns
        ----------
        bool
            True for equality.
        '''
        if not isinstance(other,MulSeries):
            return False
        else:
            return self.ds.equals(other.ds) and self.index.equals(other.index) and self.name.equals(other.name)

    def copy(self,data_copy=True):
        '''
        Create a deep copy of MulSeries.

        Parameters
        ------------
        data_copy : bool, default True
            Whether to create a deep copy of the ``.values`` attribute.
        
        Returns
        ------------
        MulSeries
            A copied mulseries.
        '''
        if data_copy:
            return MulSeries(self.__ss.copy().values,
                         index=self.index,
                         name=self.name.copy())
        else:
            return MulSeries(self.values,
                         index=self.index,
                         name=self.name,
                         index_copy=True,
                         name_copy=True,
                         data_copy=False)
    
    def __iter__(self):
        '''
        Return an iterator of the values.

        Use `Series.__iter__ <https://pandas.pydata.org/docs/reference/api/pandas.Series.__iter__.html#pandas.Series.__iter__>`_ of the values series under the hood. 
        '''
        return self.__ss.__iter__()


    def __getitem__(self,key):
        if isinstance(key,MulSeries):
            key = key.ds
        new_ss = self.__ss[key]
        if(isinstance(new_ss,pd.Series)):
            idx_new = self.mindex.loc[key]
                # print('ok')
            ms = MulSeries(new_ss,
                                index=idx_new,
                                name=self.name,
                                index_init='override')
            return ms
        else:
            return new_ss
    
    def __setitem__(self,key, values):
        if isinstance(key,MulSeries):
            key = key.ds
        self.__ss[key] = values
        if not cmm.array_like(key) and key not in self.pindex:
            self.index.loc[key] = [None]*self.index.shape[1]
    
    def _xloc_get_factory(self,attr):
        def _xloc_get(key):
            if isinstance(key,MulSeries):
                key = key.ds
            new_ss = getattr(self.__ss,attr)[key]
            if(isinstance(new_ss,pd.Series)):
                idx_new = getattr(self.mindex,attr)[key]
                ms = MulSeries(new_ss,
                                    index=idx_new,
                                    name=self.name,
                                    index_init='override')
                return ms
            else:
                return new_ss
        return _xloc_get
    
    def _xloc_set_factory(self,attr):
        def _xloc_set(key,values):
            if isinstance(key,MulSeries):
                key = key.ds
            getattr(self.__ss,attr)[key] = values
            if attr == 'loc' and not cmm.array_like(key) and key not in self.pindex:
                self.index.loc[key] = [None]*self.index.shape[1]
        return _xloc_set

    def _mloc2pos(self,key):
        nx = cmm._mloc_idx(key,self.index)
        return nx
    
    def _mloc_get(self,key):
        if key == slice(None):
            return self.iloc[:]
        else:
            nx = self._mloc2pos(key)
            # print(nx)
            return self.iloc[nx]
    
    def _mloc_set(self,key,values):
        if key == slice(None):
            self.iloc[:] = values
        else:
            nx = self._mloc2pos(key)
            self.iloc[nx] = values
    
    def _nloc2pos(self,key:dict):
        return cmm._nloc_idx(key,self.index)
    
    def _nloc_get(self,key):
        if isinstance(key,dict):
            nx = self._nloc2pos(key)
            return self.iloc[nx]
        else:
            return self._mloc_get(key)
    
    def _nloc_set(self,key,values):
        if isinstance(key,dict):
            nx = self._nloc2pos(key)
            self.iloc[nx] = values
        else:
            self._mloc_set(key,values)


    def __fill_cols(self,col_fill,cols,inplace):
        if isinstance(col_fill,pd.Series) or \
            isinstance(col_fill,pd.DataFrame):
            if isinstance(col_fill,pd.Series):
                col_fill = pd.DataFrame(col_fill).transpose()
            col_fill = cmm.test_idx_eq(col_fill,cols,copy=False)

            col_fill = cmm.test_idx_eq(col_fill,self.name.index,indexType='columns',copy=False)
            
            mcols = pd.DataFrame(self.name).transpose()
            mcols = pd.concat([col_fill,mcols],axis=0)
            return mcols
        else:
            mcols = pd.DataFrame(self.name)
            for i, col in enumerate(cols):
                mcols.insert(i,col,col_fill,allow_duplicates=True)
            return mcols.transpose()
            
    def reset_index(self,columns=None, drop=False, 
                    inplace=False, col_fill=''):
        '''
        Reset the columns of the index dataframe as the columns of the mulseries.

        Parameters
        ----------
        columns : column name(s) of the index dataframe.
            If this argument is None, reset the index of the index dataframe. If the name of this index is None, it will be named as "primary_index". If "primary_index" exists in the primary columns, it will be named as "primary_index_1" and so on.
        drop : bool, default False
            Just reset the index, without inserting index dataframe's column(s) as column(s) in the new MulDataFrame.
        inplace : bool, default False
            Modify the MulSeries in place (do not create a new object).
        col_fill : object, default ''
            A scalar, a pandas Series or a pandas DataFrame to fill in the columns dataframe of the new MulDataFrame for the inserted values. If the argument is a Series or a DataFrame, its index should align with the index of the mulseries' name (which is a pandas series) in the same way as the align mode in the :doc:`constructor <mulseries>`.

        Returns
        --------
        MulSeries, MulDataFrame or None
            The return value behaves similarly to `Series.reset_index <https://pandas.pydata.org/docs/reference/api/pandas.Series.reset_index.html>`_.
        
        Examples
        ---------
        >>> import muldataframe as md
        >>> index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
        >>> name = pd.Series([5,7],
                        index=['f','g'], name='c')
        >>> ms = MulSeries([1,8,9],index=index,name=name)
        >>> ms.reset_index()
        (3, 2)    g                7
                  f                5
                    primary_index  c
        --------  --------------------
           x  y     primary_index  c
        0  1  2   0             a  1
        1  3  6   1             b  8
        2  5  6   2             b  9

        Add a col_fill:

        >>> ss_fill = pd.Series([8,9],index=['g','f'],name='primary_index'))
        >>> ms.reset_index(col_fill=ss_fill)
        (3, 2)    g             8  7
                  f             9  5
                    primary_index  c
        --------  ---------------------
           x  y     primary_index  c
        0  1  2   0             a  1
        1  3  6   1             b  8
        2  5  6   2             b  9
        '''
        if columns is None:
            if self.mindex.index.name is None:
                indexName = cmm.get_index_name('index',
                                               self.mindex.columns)
            else:
                indexName = self.mindex.index.name
            mselect = pd.DataFrame(self.mindex.index,
                                   index=self.mindex.index,
                                   columns=[indexName])
        else:
            mselect = self.mindex[columns]
            if isinstance(mselect,pd.Series):
                mselect = pd.DataFrame(mselect)
        if inplace:
            if columns is not None:
                self.mindex.drop(columns,axis=1,inplace=True)
            if not drop:
                raise TypeError('Cannot reset_index inplace on a MulSeries to create a MulDataFrame')
            if columns is None:
                self.mindex.index = range(self.shape[0])
        else:
            if columns is not None:
                mkeep = self.mindex.drop(columns,axis=1)
            else:
                mkeep = self.mindex.copy()
                mkeep.index = range(self.shape[0])
            if not drop:
                mcols = self.__fill_cols(col_fill,mselect.columns,
                                         False)
                df = pd.concat([mselect,self.ds],axis=1)
                # print(df,mcols)
                return md.MulDataFrame(df.values,index=mkeep,columns=mcols,
                              index_copy=False,columns_copy=False)
            else:
                self2 = self.copy()
                self2.index = mkeep
                return self2


    

    def call(self,func,*args,**kwargs):
        '''
        Apply a function to the values series and returns the result as a scalar or a MulSeries with the index dataframe properly arranged.

        Parameters:
        -------------
        func : function or str
            A function applied to the values series of the MulSeries. The function should return a scalar, or a pandas Series. 
            
            - If a Series is returned, it must have the same index as the primary index (order can be different if there are no duplicate values in the primary index).
            - If ``func`` is a string, it must be a valid method name of ``pandas.Series``. The method should saftisfy the same requirement as above.
        \*args : positional arguments to the function
            The MulSeries is the 1st positional argument to the function. \*args are from the 2nd positional argument onwards.
        \*\*kwargs : keyword arguments to the function
            keyword arguments to the function.

        Returns
        -----------
        scalar or MulSeries
            If the return value is a MulSeries, it should have the same index dataframe as the caller.


        Examples
        ----------
        >>> import pandas as pd
        >>> import muldataframe as md
        >>> import numpy as np
        >>> index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
        >>> name = pd.Series([5,7],
                        index=['f','g'],
                        name='c')
        >>> ms = MulSeries([1,8,9],index=index,name=name)
        >>> ms.call(np.power,2)
        (3,)      g  7
                  f  5
                     c
        -------  ------
           x  y      c
        a  1  2  a   1
        b  3  6  b  64
        b  5  6  b  81
        '''
        # if 'unsafe' in kwargs and kwargs['unsafe']:
        # consider to change to self.ss to improve safety?
        args = list(args)
        if len(args) > 0 and (isinstance(args[0],MulSeries) or \
            isinstance(args[0],md.MulDataFrame)):
            args[0] = args[0].ds
        if len(args) > 0 and hasattr(md,'__pandas_priority__') \
            and args[0].__pandas_priority__ > self.__pandas_priority__:
            return NotImplemented
        
        self.__ss._update_super_index()
        if isinstance(func,str):
            if cmm.is_pandas_method(self,func):
                res = getattr(self.__ss,func)(*args,**kwargs)
            else:
                raise ValueError(f'If func is a string, it must be a valid method name of pandas.Series')
        else:
            res = func(self.__ss,*args,**kwargs)
        errMsg = f'Currently, {self.__class__} only supports operators or functions that return a scalar value or a pandas series with the same primary index (order can be different if there are no duplicate values) in its .call() method.'
        # else:
        #     res = func(self.ss,*args,**kwargs)
        # print(res)
        if isinstance(res,pd.DataFrame):
            # print('dataframe',res)
            # have to raise error here because pandas does not support muldataframe in its __radd__ like functions.
            raise NotImplementedError(errMsg)
            # return NotImplemented
        elif isinstance(res,pd.Series):
            if res.shape[0] == self.shape[0]:
                if not res.index.equals(self.index.index):
                    try:
                        # res2 = self.loc[res.index]
                        new_idx = cmm.align_index_in_call(res.index,self,
                                                          'index')
                        if new_idx.shape[0] == self.shape[0]:
                            return MulSeries(res.values,
                                             index=new_idx,
                                             name=self.name,
                                             index_copy=False)
                        # if res2.shape[0] == self.shape[0]:
                        #     return res2
                        else:
                            raise NotImplementedError(errMsg)
                    except:
                        raise NotImplementedError(errMsg)
                else:
                    if res.name == self.name.name:
                        name = self.name.copy()
                    else:
                        name = pd.Series([],name=res.name)
                    return MulSeries(res,
                                    index=self.index,
                                    name=name,
                                    index_init='override')
            else:
                # print('shape',res.shape,self.shape)
                raise NotImplementedError(errMsg)
        else:
            return res

    def groupby(self,by=None,agg_mode:cmm.IndexAgg='same_only',keep_primary=False):
        '''
        Group MulSeries by its index dataframe using a mapper or the index dataframe's columns.

        The function uses the `DataFrame.groupby <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html#pandas.DataFrame.groupby>`_ method of the index dataframe to create groups under the hood. The values of the MulSeries are grouped accordingly. It returns a :doc:`MulGroupBy <../groupby/indices>` object that contains information about the groups.

        Parameters
        ------------
        by : None, mapping, function, label, pd.Grouper or list of such
            Please refers to `DataFrame.groupby <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html#pandas.DataFrame.groupby>`_ for detailed information on this argument. The difference to the :code:`by` argument in DataFrame.groupby is that if it is None, uses the primary index to group the MulSeries.
        
        agg_mode : 'same_only', 'list','tuple', default to 'same_only'
            Determine how to aggregate column values in the index dataframe that are not the same in each group when calling numpy functions on or using the :doc:`call <../groupby/indices>` method of the MulGroupBy object.

             - ``'same_only'``: only keep columns that have the same values within each group. 
             - ``'list'``: put columns that do not have the same values within a group into a list. 
             - ``'tuple'``: similar to 'list', but put them into a tuple.

        keep_primary : bool, default False
            Whether to keep primary index in the index dataframe in each group. If ``True``, the primary index will be reset as a column and kept in the grouped dataframes.  If the name of the primary index or columns is ``None``, ``"primary_index"`` will be used as its name.

        Returns
        -----------
        MulGroupBy
            A :doc:`MulGroupBy <../groupby/indices>` object that contains information about the groups.
                

        Examples
        ------------
        >>> import muldataframe as md
        >>> import pandas as pd
        >>> index = pd.DataFrame([['a','b','c'],
                                  ['g','b','f'],
                                  ['b','g','h']],
                        columns=['x','y','z'])
        >>> name = pd.Series(['a','b'],index=['e','f'],name='cc')
        >>> ms = MulSeries([1,2,3],index=index,name=name)
        >>> for key, group in ms.groupby('y'):
        ...     print(key,'\\n',group)
        ...     break
        b
        (2,)        f  b
                    e  a
                       cc
        ----------  ------
           x  y  z     cc
        0  a  b  c  0   1
        1  g  b  f  1   2
        >>> ms.groupby('y').sum()
        (2,)             f   b
                         e   a
                            cc
        ---------------  ------
        Empty DataFrame     cc
        Columns: []      y
        Index: [b, g]    b   3
                         g   3
        >>> ms.groupby('y',agg_mode='list').sum()
        (2,)               f   b
                           e   a
                              cc
        -----------------  ------
                x       z     cc
        y                  y
        b  [a, g]  [c, f]  b   3
        g       b       h  g   3
        '''
        return cmm.groupby(self,'index',by=by,
                           keep_primary=keep_primary,agg_mode=agg_mode)
    
    
    def query(self,index=None, **kwargs):
        '''
        Query the index dataframe of a MulSeries and return the the query result as a MulSeries.

        The function uses the ``pandas.DataFrame.query`` method under the hood.

        Parameters
        -----------
        index : None or str
            The query string to evaluate for the index dataframe. Check `DataFrame.query <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html>`_ for detailed specification of this argument.
        kwargs : any
            The same ``kwargs`` passed to `DataFrame.query <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html>`_ including the ``inplace=False`` argument.

        Returns
        ----------
        MulSeries or None
            None if ``inplace=True.``


        Examples
        ---------
        >>> index = pd.DataFrame([['a','b','c'],
                                  ['g','b','f'],
                                  ['b','g','h']],
                        columns=['x','y','z'])
        >>> name = pd.Series(['a','b'],index=['e','f'],name='cc')
        >>> ms = MulSeries([1,2,3],index=index,name=name)
        >>> ms.query('y == "b"')
        (2,)        f   b
                    e   a
                       cc
        ----------  ------
           x  y  z     cc
        0  a  b  c  0   1
        1  g  b  f  1   2
        '''
        if 'inplace' in kwargs:
            inplace = kwargs['inplace']
        else:
            inplace = False
        kwargs['inplace']=False

        if index is not None:
            rowIdx = cmm._query_index(self.mindex,index,**kwargs)
        else:
            rowIdx = slice(None)

        if not inplace:
            return self.iloc[rowIdx]
        else:
            self.__ss = self.__ss.iloc[rowIdx]
            self.index = self.index.iloc[rowIdx]
    

    def drop_duplicates(self,keep='first', inplace=False):
        '''
        Return MulSeries with duplicate values removed. 
        
        It is similar to `Series.drop_duplciates <https://pandas.pydata.org/docs/reference/api/pandas.Series.drop_duplicates.html>`_ except it returns a MulSeries with the index dataframe properly sliced.

        Parameters
        -----------
        keep : {'first', 'last', False}, defaul t 'first'
            Method to handle dropping duplicates:

            - 'first' : Drop duplicates except for the first occurrence.
            - 'last' : Drop duplicates except for the last occurrence.
            - ``False`` : Drop all duplicates.
        inplace : bool, default False
            If True, performs operation inplace and returns None.
        
        Returns:
        ----------
        MulSeries or None
            If inplace=True, returns None. Otherwise, returns a MulSeries. The MulSeries' index dataframe is properly sliced according to removed values.

        '''
        self.__ss._update_super_index()
        bidx = self.__ss.duplicated(keep=keep)
        bidx_keep = ~bidx
        new_ss = self.__ss.loc[bidx_keep]

        if inplace:
            # primary_index = self.index.index
            # primary_columns = self.columns.index
            self.__ss = None
            self.index = self.index.loc[bidx_keep]
            self.__ss = ValSeries(self,new_ss)
        else:
            return MulSeries(new_ss.values,
                        index=self.index.loc[bidx_keep],
                        name=self.name)
    
    def sort_values(self,*args,**kwargs):
        '''
        Sort by the values in the values Series.

        The input parameters are exactly the same as `pandas.Series.sort_values <https://pandas.pydata.org/docs/reference/api/pandas.Series.sort_values.html>`_ method except the return value is a mulseries.

        Parameters
        ------------
        Exactly the same as those in `pandas.Series.sort_values <https://pandas.pydata.org/docs/reference/api/pandas.Series.sort_values.html>`_.

        Returns
        ---------
        MulSeries
            A MulSeries object with the values series and the index dataframe sorted.

        Examples
        ---------
        >>> index = pd.DataFrame([['a','b','c'],
                                  ['g','b','f'],
                                  ['b','g','h']],
                        columns=['x','y','z'])
        >>> name = pd.Series(['a','b'],index=['e','f'],name='cc')
        >>> ms = MulSeries([1,2,3],index=index,name=name)
        >>> ms.sort_values(ascending=False)
        (3,)        f   b
                    e   a
                       cc
        ----------  ------
           x  y  z     cc
        2  b  g  h  2   3
        1  g  b  f  1   2
        0  a  b  c  0   1
        '''
        if self.pindex.is_unique:
            return self.call('sort_values',*args,**kwargs)
        else:
            pindex = self.pindex
            self.pindex = range(self.shape[0])
            res = self.call('sort_values',*args,**kwargs)
            res.pindex = pindex[res.pindex]
            self.pindex = pindex
            return res


ops = ['add','sub','mul','div','truediv','floordiv','mod','pow','eq','le','lt','gt','ge','ne']
for op in ops:
    op_attr = '__'+op+'__'
    def call_op_factory(op_attr):
        def call_op(self,other):
            if 'eq__' in op_attr:
                return self.equals(other)
            elif 'ne__' in op_attr:
                return not self.equals(other)
            else:
                return self.call(op_attr,other)
        return call_op
    setattr(MulSeries,op_attr,call_op_factory(op_attr))
    r_op_attr = '__r'+op+'__'
    setattr(MulSeries,r_op_attr,call_op_factory(r_op_attr))


# ops = []
# for op in ops:
#     op_attr = '__'+op+'__'
#     def call_op_factory(op_attr):
#         def call_op(self,other):
#             func = getattr(pd.Series,op_attr)
#             # print(op_attr,func)
#             return self.call(func,other)
#         return call_op
#     setattr(MulSeries,op_attr,call_op_factory(op_attr))


ValSeries = vfb.ValFrameBase_factory(pd.Series)
# def _update_super_index(self):
#     self.index = self.parent.mindex.index
#     self.name = self.parent.name.name
# ValSeries._update_super_index = _update_super_index

