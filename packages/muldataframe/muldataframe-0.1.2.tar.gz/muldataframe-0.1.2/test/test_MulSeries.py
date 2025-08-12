
import pandas as pd
from .lib import eq
import pytest
import numpy as np
import muldataframe as md
MulDataFrame = md.MulDataFrame
MulSeries = md.MulSeries

def test_init():
    index = pd.DataFrame([['a','b'],['c','d']])
    with pytest.raises(IndexError):
        MulSeries([1,2,3],index=index)
    
    index = pd.DataFrame([['a','b'],['c','d']],
                         index=['e','f'])
    assert eq(MulSeries(pd.Series([1,2],index=['f','e']),
                        index=index).values,[2,1])
    assert eq(MulSeries({'f':1,'e':2},index=index,index_init='align').values,[2,1])
    assert eq(MulSeries({'f':1,'e':2,'g':3},index=index,index_init='align').values,[2,1])

    with pytest.raises(IndexError):
        MulSeries(pd.Series([1,2,3],index=['f','e','f']),
                        index=index)
    
    index = pd.DataFrame([['a','b'],['c','d'],
                          ['g','h']],
                         index=['e','f','f'])
    assert eq(MulSeries({'f':1,'e':2},index=index,index_init='align').values,[2,1,1])
    
    with pytest.raises(IndexError):
        MulSeries({'f':1,'e':2,'g':3},index=index)

def test_getattr():
    index = pd.DataFrame([['a','b'],['c','d']],
                         index=['e','f'])
    ms = MulSeries(pd.Series([1,2],index=['e','f']), 
                        index=index)

    ss = ms.ss
    ss.index = ['k','l']
    assert eq(ms.index.index.values,['e','f'])
    ss.iloc[0] = 5
    assert ms.iloc[0] == 1

    ss = ms.ds
    ss.index = ['k','l']
    assert eq(ms.index.index.values,['e','f'])
    ss.iloc[0] = 5
    assert ms.iloc[0] == 5

    assert ms.shape == (2,)

    assert ms.mindex.equals(ms.index)
    assert ms.midx.equals(ms.index)
    assert ms.mname.equals(ms.name)
    assert ms.mname.name == ms.pname


    index = pd.DataFrame([['a','b'],['c','d'],
                          ['g','h']],
                         index=['e','f','f'])
    ms = MulSeries(pd.Series([1,2,3],index=['e','f','f']), 
                        index=index)
    ms2 = ms['f']
    index = pd.DataFrame([['c','d'],
                          ['g','h']],
                         index=['f','f'])
    mse = ms = MulSeries(pd.Series([2,3],index=['f','f']), 
                        index=index)
    assert ms2 == mse



def test_setattr():
    index = pd.DataFrame([['a','b'],['c','d']],
                         index=['e','f'])
    ms = MulSeries(pd.Series([1,2],index=['e','f']), 
                        index=index)
    index = pd.DataFrame([['a','b'],
                          ['c','d'],
                          ['e','f']],
                          index=['g','h','i'])
    with pytest.raises(AttributeError):
        ms.ss = pd.Series([1,5])
    with pytest.raises(IndexError):
        ms.index = index
    

def test_ops_get_set_items():
    index = pd.DataFrame([['a','b'],['c','d']],
                         index=['e','f'])
    ms = MulSeries(pd.Series([1,3],index=['e','f']), 
                        index=index)
    ms2 = MulSeries(pd.Series([1,3],index=['e','f']), 
                        index=index)
    assert ms.equals(ms2)
    assert ms == ms2
    assert ms != pd.Series([1,3],index=['e','f'])

    # print('\n',ms)
    ms3 = ms.copy()
    ms3['g'] = 9
    assert ms3.shape == (3,)
    assert ms3['g'] == 9
    assert eq(ms3.index.loc['g'].values, [None]*2)


    def foo(ss):
        return ss.iloc[::-1]
    msf = ms.call(foo)
    assert eq(msf.values,[3,1])

    def foo2(ss):
        return ss.iloc[[0,1,1]]
    with pytest.raises(NotImplementedError):
        msf = ms.call(foo2)

    def foo3(ss):
        return pd.Series([1,3],index=['a','b'])
    with pytest.raises(NotImplementedError):
        msf = ms.call(foo3)

    ms2['e'] = 5
    assert ms != ms2
    assert ms2.ss.iloc[0] == 5
    assert ms2['e'] == 5

    ms3 = ms+ms2
    assert eq(ms3.values,[6,6])

    mse = MulSeries(pd.Series([1,3],index=['e','f']), 
                        index=index)
    ms2e = MulSeries(pd.Series([5,3],index=['e','f']), 
                        index=index)
    assert mse == ms
    assert ms2e == ms2

    msa = ms*2
    msb = 2*ms
    assert eq(msa.values,[2,6])
    assert msa == msb

    ms2 = MulSeries(pd.Series([1,3],index=['e','f']), 
                        index=index)
    ms2.index.index = ['e','k']

    assert not ms2.index.equals(index)
    with pytest.raises(NotImplementedError):
        ms + ms2
    
    index = pd.DataFrame([['a','b'],['c','d']],
                         index=['e','f'])
    ms = MulSeries(pd.Series([1,3],index=['e','f']), 
                        index=index,
                        index_copy=False)
    ms.index.index = ['e','k']
    assert eq(index.index.values,['e','k'])

    ms.index.index = ['e','f']
    msc = ms.call(np.power,2)
    assert eq(msc.values,[1,9])

    msc = ms.call(np.sum)
    assert msc == 4

    msc = ms.call(np.add,[5,6])
    # print(msc)
    assert eq(msc.values,[6,9])

    index = pd.DataFrame([['a','b'],['c','d'],
                          ['e','f']],
                         index=['a','b','b'])
    ms = MulSeries(pd.Series([1,3,5],
                    index=['a','b','b']), 
                        index=index,
                        name='abc')
    msp = ms+pd.Series([1,3,5],index=['a','b','b'])
    assert eq(msp.values,[2,6,10])
    assert msp.name.name is None

    with pytest.raises(NotImplementedError):
        ms+pd.Series([1,3,5],index=['b','a','b'])

    with pytest.raises(NotImplementedError):
        ms.call(foo)
    
    def to_df(ss):
        return pd.DataFrame([])
    
    with pytest.raises(NotImplementedError):
        ms.call(to_df)

    index = pd.DataFrame([['a','b'],['c','d']],
                         index=['e','f'])
    ms = MulSeries(pd.Series([1,3],index=['e','f']), 
                        index=index)
    assert ms.mean() == 2

    ms2 = ms.multiply(2)
    assert isinstance(ms2,MulSeries)
    assert eq(ms2.values,[2,6])

    ms2 = ms.log2()
    assert ms2.iloc[0] == 0


def test_loc():
    index = pd.DataFrame([['a','b','c'],
                        [ 'g','b','f'],
                        [ 'b','g','h']],
                        columns=['x','y','y'],
                        index=['k','l','m'])
    name = pd.Series(['a','b'],index=['e','f'],name='cc')
    ms = MulSeries([1,2,3],index=index,name=name)
    
    ms2 = ms.copy()
    ms2['p'] = 9
    assert ms2.shape == (4,)
    assert eq(ms2.index.loc['p'].values, [None]*3)
    assert ms2['p'] == 9
    # print('\n',ms2)

    assert ms.loc['k'] == 1
    assert eq(ms.loc[['m','l']].values, [3,2])

    ms.index.index = ['a','b','b']
    assert eq(ms.loc['b'].values, [2,3])
    assert eq(ms.index.index.values,['a','b','b'])
    
    ms.loc['b'] = 5
    assert eq(ms.values, [1,5,5])

    ms.loc['b'] = [5,6]
    assert eq(ms.values, [1,5,6])

    ms.loc[['a','b']] = [1,2,3]
    assert eq(ms.values, [1,2,3])
    assert ms.values[-1] == 3



def test_mloc_nloc_get():
    index = pd.DataFrame([['a','b','c'],
                        [ 'g','b','f'],
                        [ 'b','g','h']],
                        columns=['x','y','y'])
    name = pd.Series(['a','b'],index=['e','f'],name='cc')
    ms = MulSeries([1,2,3],index=index,name=name)
    # print(type(ms.mloc[[None,'b']].values))
    assert eq(ms.mloc[:].values,[1,2,3])

    assert eq(ms.mloc[[...,'b']].values,
                      [1,2])
    
    assert eq(ms.nloc[:].values,[1,2,3])

    assert eq(ms.nloc[[...,'b']].values,
                      [1,2])
    # print('\n',ms.mloc[[None,'b']])
    assert eq(ms.mloc[[..., ..., ['h','f']]].values,[3,2])

    assert ms.mloc[['g', ..., ['h','f']]] == 2

    with pytest.raises(KeyError):
        ms.mloc[['a', ..., ['h','f']]]
    with pytest.raises(KeyError):
        ms.mloc[[['a','g'], ..., ['h','f']]]
    with pytest.raises(IndexError):
        ms.mloc[[['a','g'], ..., ['h','f'],'kk']]
    
    assert ms.mloc[['b']] == 3
    with pytest.raises(KeyError):
        ms.mloc[{'y':'b'}]

    assert eq(ms.mloc[{'y':['c','h']}].values,[1,3])
    assert ms.mloc[{'x':'b'}] == 3

    assert eq(ms.mloc[[['a','g'], ..., ['f','c']]].values,[2,1])
    assert eq(ms.mloc[[['g','a'], ..., ['c','f']]].values,[1,2])

    assert eq(ms.mloc[{'y':['c','h'],'x':['b','a']}].values,[3,1])
    # print('\n',ms.mloc[{'y':['c','h'],'x':['b','a']}])
    assert eq(ms.mloc[{'y':['h','c'],'x':['a','b']}].values,[1,3])

    assert eq(ms.nloc[{2:['c','h'],0:['b','a']}].values,[3,1])
    assert eq(ms.nloc[{2:['h','c'],0:['a','b']}].values,[1,3])


    index = pd.DataFrame([['a','b','c'],
                        [ 'g','b','f'],
                        [ 'b','g','h']],
                        columns=['x','y','z'])
    name = name = pd.Series(['a','b'],index=['e','f'],name='cc')
    ms = MulSeries([1,2,3],index=index,name=name)
    assert eq(ms.mloc[[..., 'b']].values,[1,2])
    
    res = ms.mloc[{'y':[True, False, True]}]
    assert eq(res.values,[1,3])

def test_mloc_nloc_set():
    index = pd.DataFrame([['a','b','c'],
                        [ 'g','b','f'],
                        [ 'b','g','h']],
                        columns=['x','y','y'])
    name = pd.Series(['a','b'],index=['e','f'],name='cc')
    ms = MulSeries([1,2,3],index=index,name=name)
    ms.mloc[[..., 'g']] = 5
    assert eq(ms.values,[1,2,5])

    ms2 = ms.copy()
    ms2.nloc[{1:'g'}] = 6
    assert eq(ms2.values,[1,2,6])
    ms2.nloc[:] = [1,2,3]

    ms.iloc[:] = [1,2,3]
    assert eq(ms.values,[1,2,3])
    ms.mloc[:] = [1,2,3]
    assert eq(ms.values,[1,2,3])

    ms.mloc[{'y':['c','f']}] = [5,6]
    assert eq(ms.values,[5,6,3])

    ms2.nloc[{2:['c','f']}] = [5,6]
    assert eq(ms2.values,[5,6,3])

    index = pd.DataFrame([['a','b','c'],
                        [ 'g','b','f'],
                        [ 'b','g','h']],
                        columns=['x','y','z'])
    name = name = pd.Series(['a','b'],index=['e','f'],name='cc')
    ms = MulSeries([1,2,3],index=index,name=name)
    ms.mloc[{'y':'b'}] = [5,6]
    assert eq(ms.values,[5,6,3])


def get_data():
    index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
    columns = pd.DataFrame([[5,7],[3,6]],
                        index=['c','d'],
                        columns=['f','g'])
    ms = MulSeries([1,8,9],index=index,name=columns.loc['c'])
    return ms,index,ms.name

def test_loc_item():
    ms,_,_ = get_data()
    ms2 = ms.loc[ms>2]
    assert eq(ms2.values, [8,9])
    assert eq(ms2.pindex.values,['b','b'])

    ms3 = ms[ms>2]
    assert ms3 == ms2

    ms[ms>2] = 5
    assert eq(ms.values,[1,5,5])

    ms.loc[ms>2] = 5
    assert eq(ms.values,[1,5,5])


def test_insert():
    ms, _, _ = get_data()
    ms2 = ms.copy()
    ms2.insert('e',7)
    # print('\n',ms2)
    assert eq(ms2.pindex.tolist(),['a','b','b','e'])
    assert eq(ms2.values, [1,8,9,7])
    assert eq(ms2.mindex.iloc[-1].values,[None]*2)

    ms2 = ms.insert('e',7,1,[8,9],False)
    # print('\n',ms2)
    assert eq(ms2.pindex.tolist(),['a','e','b','b'])
    assert eq(ms2.values, [1,7,8,9])
    assert eq(ms2.mindex.iloc[1].values,[8,9])


def test_drop():
    ms, _, _ = get_data()
    ms2 = ms.copy()
    ms3 = ms2.drop('b')
    assert ms2 == ms
    assert ms3.shape == (1,)
    assert ms3.index.shape == (1,2)
    # print('\n',ms3)

    ms2.drop('a',inplace=True)
    assert ms2.shape == (2,)
    assert eq(ms2.values, [8,9])

    ms2 = ms.drop(6,mloc='y')
    assert ms2.shape == (1,)
    assert ms2.index.shape == (1,2)


def get_data2():
    index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
    columns = pd.DataFrame([[5,7],[3,6]],
                        index=['c','d'],
                        columns=['f','g'])
    md = MulDataFrame([[1,2],[8,9],[8,10]],index=index,
                    columns=columns)
    return md,index,columns

def test_reset_index():
    md,index,name = get_data()
    md2 = md.reset_index()
    # print('\n',md2)
    assert md2.mindex.shape == md.mindex.shape
    assert eq(md2.mindex.index.values,[0,1,2])
    assert eq(md2.mcols.index, ['primary_index','c'])
    assert eq(md2.mcols.iloc[0],['',''])
    assert md2.mcols.shape == (2,2)

    ss_fill = pd.Series(
        [8,9],index=['g','f'],name='primary_index')
    msx = md.reset_index(col_fill=ss_fill)
    # print('\n',msx)
    assert msx.columns.columns.equals(md.name.index)
    assert eq(msx.columns.loc['primary_index'].values,[9,8])


    with pytest.raises(TypeError):
        md.reset_index(inplace=True,col_fill=0)

    md,index,columns = get_data()
    md2 = md.reset_index(drop=True)
    assert md.mindex.shape == md2.mindex.shape
    assert md.shape == md2.shape
    assert eq(md2.index.index,[0,1,2])

    md2 = md.reset_index(['x','y'])
    # print(md,'\n',md2)
    assert md2.mindex.shape == (3,0)
    assert md2.mcols.shape == (3,2)
    assert md2.mindex.index.equals(md.mindex.index)
    
    md, index, columns = get_data2()
    md2 = md.set_index('c')
    ss = md.mcols.loc['c']
    ms = md2['d']
    md3 = ms.reset_index('c',col_fill=ss)
    assert md3 == md

    md2 = md.reset_index('x')
    md3 = md2.set_index(['x','c'])
    df = md2.mcols.loc[['x','c']]
    md4 = md3['d']
    md5 = md4.reset_index(['x','c'],col_fill=df)
    assert md5 == md2

    with pytest.raises(IndexError):
        md4.reset_index(['x','c'],col_fill=df.loc[['x','c','c']])
    df.index = ['k','m']
    with pytest.raises(KeyError):
        md2.reset_index(['c','d'],col_fill=df)

def test_drop_duplicates():
    index = pd.DataFrame([['a','b','c'],
                        [ 'g','b','f'],
                        [ 'b','g','h']],
                        columns=['x','y','z'])
    name = pd.Series(['a','b'],index=['e','f'],name='cc')
    ms = MulSeries([1,2,2],index=index,name=name)

    ms2 = ms.drop_duplicates()
    assert ms2.shape == (2,)
    assert ms2.mindex.shape == (2,3)
    assert eq(ms2.mindex.index,[0,1])

    ms.drop_duplicates(inplace=True)
    ms2 = ms
    assert ms2.shape == (2,)
    assert ms2.mindex.shape == (2,3)
    assert eq(ms2.mindex.index,[0,1])


def test_query():
    index = pd.DataFrame([['a','b','c'],
                        [ 'g','b','f'],
                        [ 'b','g','h']],
                        columns=['x','y','z'])
    name = name = pd.Series(['a','b'],index=['e','f'],name='cc')
    ms = MulSeries([1,2,3],index=index,name=name)
    ms2 = ms.query('y == "b"')
    assert ms2.shape == (2,)
    assert eq(ms2.values,[1,2])
    
    ms2 = ms.copy()
    ms2.query('y == "b"',inplace=True)
    assert ms2.shape == (2,)
    assert eq(ms2.values,[1,2])

    ms2 = ms.query()
    assert ms2 == ms


def test_groupby():
    index = pd.DataFrame([['a','b','c'],
                        [ 'g','b','f'],
                        [ 'b','g','h']],
                        columns=['x','y','z'])
    name = name = pd.Series(['a','b'],index=['e','f'],name='cc')
    ms = MulSeries([1,2,3],index=index,name=name)

    # for key, group in ms.groupby('y'):
    #     print(key,'\n',group)
    #     break

    # print('\n',ms.groupby('y').sum())
    # print('\n',ms.groupby('y',agg_mode='list').sum())


    assert eq(ms.groupby('y').sum().values,[3,3])
    ms2 = ms.copy()
    ms2.index.set_index('x',inplace=True)
    res = ms2.groupby('y').mean()
    assert eq(res.values,[1.5,3])
    assert eq(res.index.index.values,['b','g'])
    assert eq(res.index.columns.values,[])

    res = ms2.groupby('y',agg_mode='list').mean()
    assert eq(res.index.columns.values,['z'])
    assert eq(res.index['z'].values[0],['c','f'])

    # print('++++++++++++++++++')
    # print('\n',ms2)
    res = ms2.groupby('y',keep_primary=True,
                      agg_mode='list').mean()
    assert eq(res.index.index.values,['b','g'])
    assert eq(res.index.columns.values,['x','z'])
    assert eq(res.index['z'].values[0],['c','f'])
    assert eq(res.index['x'].values[0],['a','g'])


    def gpAdd(gp):
        if gp.mindex['y'].iloc[0] == 'b':
            return gp+5
        else:
            return gp
    msa = ms.groupby('y').call(gpAdd,use_mul=True)
    assert eq(msa.values,[6,7,3])


def test_sort_values():
    import muldataframe as md
    index = pd.DataFrame([[1,2],[3,6],[5,6]],
                        index=['a','b','b'],
                        columns=['x','y'])
    name = pd.Series([5,7],
                            index=['f','g'],
                            name='c')
    ms = MulSeries([8,1,9],index=index,name=name)
    
    ms2 = ms.sort_values()
    # print('\n',ms2)
    assert eq(ms2.pindex,['b','a','b'])
    assert eq(ms2.values.tolist(),[1,8,9])

    index = pd.DataFrame([[1,2],[3,6],[5,6]],
                        index=['a','b','c'],
                        columns=['x','y'])
    ms.index = index
    ms2 = ms.sort_values()
    assert eq(ms2.pindex,['b','a','c'])
    assert eq(ms2.values.tolist(),[1,8,9])
