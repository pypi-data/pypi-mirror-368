# from ..MulSeries import MulSeries
# from ..MulDataFrame import MulDataFrame
import pandas as pd
from .lib import eq
import pytest
import numpy as np
import muldataframe as md
MulDataFrame = md.MulDataFrame
MulSeries = md.MulSeries

#TODO: mloc set

def get_data():
    index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
    columns = pd.DataFrame([[5,7],[3,6]],
                        index=['c','d'],
                        columns=['f','g'])
    md = MulDataFrame([[1,2],[8,9],[8,10]],index=index,
                    columns=columns)
    return md,index,columns


def test_loc_item():
    mf, _, _ = get_data()
    mf2 = mf[mf['c']>1]
    assert eq(mf2.values,[[8,9],[8,10]])

    mf3 = mf.loc[mf['c']>1]
    assert mf2 == mf3

    mf2 = mf.loc[:,mf.loc['a']>1]
    assert eq(mf2.values,[[2],[9],[10]])

    mf3 = mf.loc[mf['c']>1,mf.loc['a']>1]
    assert eq(mf3.values,[[9],[10]])

    mf[mf['c']>1] = 5
    assert eq(mf.iloc[1:].values,[[5,5],[5,5]])

    
    # print('\n',mf.loc[mf['c']>1,mf.loc['a']>1])
    mf.loc[mf['c']>1,mf.loc['a']>1] = [[8],[9]]
    # assert eq(mf.values,[[1,2],[5,8],[5,9]])



def test_drop():
    ms, _, _ = get_data()
    ms2 = ms.copy()
    ms3 = ms2.drop('b')
    assert ms2 == ms
    assert ms3.shape == (1,2)
    assert ms3.index.shape == (1,2)

    ms2 = ms.drop(2,mloc='y')
    assert ms2.shape == (2,2)
    assert ms2.index.shape == (2,2)
    assert eq(ms2.pindex.values,['b','b'])
    assert ms2.pindex.name == ms.pindex.name
    assert ms2.mcols.shape == (2,2)

    ms.drop(5,mloc='f',inplace=True,axis=1)
    assert ms.shape == (3,1)
    assert ms.mcols.shape == (1,2)
    assert eq(ms.values,[[2],[9],[10]])
    mso, _, _ = get_data()
    assert ms.pcols.name == mso.pcols.name
    assert ms.mcols.shape == (1,2)


def test_loc():
    md, _, _ = get_data()
    md.loc['e'] = [5,7]
    assert eq(md.loc['e'].values,[5,7])
    assert md.shape == (4,2)
    assert eq(md.mindex.loc['e'].values,[None]*2)

    md, _, _ = get_data()
    md.loc['e'] = MulSeries([5,7],
        index=pd.DataFrame(index=['c','d']),
        name=pd.Series([8,9],index=['x','y']))
    # print('\n',md)
    assert eq(md.loc['e'].values,[5,7])
    assert md.shape == (4,2)
    assert eq(md.mindex.loc['e'].values,[8,9])

    md, _, _ = get_data()
    md.loc[:,'e'] = MulSeries([5,7,8],
        index=pd.DataFrame(index=['a','b','b']),
        name=pd.Series([8,9],index=['f','g']))
    # print('\n',md)
    assert eq(md.loc[:,'e'].values,[5,7,8])
    assert md.shape == (3,3)
    assert eq(md.mcols.loc['e'].values,[8,9])

    md, _, _ = get_data()
    md.loc[:,['c','d']] = [[1,2],[5,5],[6,7]]
    assert eq(md.values,[[1,2],[5,5],[6,7]])


def test_insert():
    mf,_,_ = get_data()
    mf2 = mf.copy()
    mf2.insert('e',[7,8,9])
    # print('\n',mf2)
    assert eq(mf2.pcolumns.tolist(),['c','d','e'])
    assert(mf2.shape == (3,3))
    assert eq(mf2.iloc[:,-1].values,[7,8,9])
    
    # assert eq(mf2.columns.loc['e'].values,[np.nan]*2)
    assert eq(mf2.columns.loc['e'].values,[None]*2)
    assert(mf2.mindex.shape == (3,2))

    mf2 = mf.insert('e',[7,8,9],inplace=False)
    assert eq(mf2.pcolumns.tolist(),['c','d','e'])
    assert (mf2.shape == (3,3))
    assert eq(mf2.iloc[:,-1].values,[7,8,9])

    mf2 = mf.insert('e',[7,8,9],name=[8,9],
                    inplace=False)
    assert eq(mf2.columns.loc['e'],[8,9])

    mf2 = mf.insert('e',
        MulSeries([7,8,9],
                  name=pd.Series([8,9],index=['f','g']),
                  index=pd.DataFrame(index=['a','b','b'])),
        inplace=False)
    assert eq(mf2.iloc[:,-1].values,[7,8,9])
    assert eq(mf2.columns.loc['e'],[8,9])
    mf3 = mf.insert('e',
        MulSeries([7,8,9],
                  name=pd.Series([8,9],index=['f','g']),
                  index=pd.DataFrame(index=['a','b','b'])),
        name=[10,12],
        inplace=False)
    assert(mf2 == mf3)

    mf2 = mf.insert('e',[7,8], axis=0,
                    inplace=False)
    assert mf2.shape == (4,2)
    assert mf2.index.shape == (4,2)
    assert eq(mf2.index.loc['e'],[None]*2)

    mf2 = mf.insert('e',[7,8], name=[9,10],
                    axis=0,
                    inplace=False)
    assert eq(mf2.index.loc['e'],[9,10])
    # print('\n',mf2)


def test_init():
    index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
    columns = pd.DataFrame([[5,7],[3,6]],
                        index=['c','d'],
                        columns=['f','g'])
    md = MulDataFrame([[1,2],[8,9],[8,10]],index=index,
                    columns=columns)
    
    index.iloc[0,0] = 7
    assert md.mindex.iloc[0,0] == 1
    md.mindex.iloc[2,0] = 8
    assert index.iloc[2,0] == 5
    columns.iloc[0,0] = 7
    assert md.mcolumns.iloc[0,0] == 5

    index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
    columns = pd.DataFrame([[5,7],[3,6]],
                        index=['c','d'],
                        columns=['f','g'])
    md = MulDataFrame([[1,2],[8,9],[8,10]],
                      index=index,
                    columns=columns,
                    both_copy=False)
    index.iloc[0,0] = 7
    assert md.mindex.iloc[0,0] == 7
    md.mindex.iloc[2,0] = 8
    assert index.iloc[2,0] == 8
    columns.iloc[0,0] = 7
    assert md.mcolumns.iloc[0,0] == 7

    index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
    md = MulDataFrame(index)
    assert md.mindex.shape == (3,0)
    assert md.mcolumns.shape == (2,0)

    # print('===================')
    md = MulDataFrame(index,index=index)
    assert md.index.index.equals(md.df.index)

    index2 = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['b','a','b'],
                     columns=['x','y'])
    with pytest.raises(IndexError):
        MulDataFrame(index,index=index2)
    md = MulDataFrame(index.values,index=index2)
    assert eq(md.mindex.index.values,['b','a','b'])
    md = MulDataFrame(index.values,index=index2,
                      index_init='override')
    assert eq(md.mindex.index.values,['b','a','b'])


    values = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['b','a','c'],
                     columns=['x','y'])
    index2 = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['b','a','b'],
                     columns=['x','y'])
    with pytest.raises(IndexError):
        MulDataFrame(values,index=index2)

    index2 = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['d','a','b'],
                     columns=['x','y'])
    index2.index.name = 'z'
    md = MulDataFrame(values,index=index2)
    # print(md.mindex.index.name)
    assert eq(md.mindex.index.values,['a','b'])
    assert md.mindex.index.name == 'z'

    md = MulDataFrame(values.transpose(),columns=index2)
    assert eq(md.mcols.index.values,['a','b'])
    assert md.mcols.index.name == 'z'

    columns2 = pd.DataFrame([[5,7],[3,6]],
                        index=['d','c'],
                        columns=['f','g'])
    md = MulDataFrame(columns,index=columns2,index_init='align')
    assert eq(md.mindex.index.values,['d','c'])


def test_get_set_attr():
    md,index,columns = get_data()
    assert eq(md.values,md.df.values)
    assert eq(md.values,md.ds.values)

    values = md.values
    dvals = md.df.values
    svals = md.ds.values
    values[0,0] = 5
    assert md.values[0,0] == 5
    assert svals[0,0] == 5
    assert dvals[0,0] == 1

    assert md.shape == (3,2)

    index2 = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['b','a','b'],
                     columns=['x','y'])
    md.index = index2
    assert md.df.index.equals(index2.index)
    md.mindex = index
    assert md.df.index.equals(index.index)

    # md.index = columns
    with pytest.raises(IndexError):
        md.index = columns


def test_get_setitem():
    md,index,columns = get_data()
    # print('\n',md)
    ss = md['c']
    assert ss.index.equals(md.mindex)
    assert isinstance(ss,MulSeries)
    assert eq(ss.values,[1,8,8])

    md.columns.index = ['c','c']
    md2 = md['c']
    assert md2 == md

    md,index,columns = get_data()
    md['c'] = [5,5,5]
    # print('================')
    assert eq(md.loc[:,'c'].values,[5,5,5])

    md,index,columns = get_data()
    md['e'] = [6,7,8]
    assert eq(md.loc[:,'e'].values,[6,7,8])
    assert md.shape == (3,3)
    assert eq(md.mcols.loc['e'].values,[None]*2)

    md,index,columns = get_data()
    md['e'] = MulSeries([6,7,8],
        index=pd.DataFrame(index=['a','b','b']),
        name=pd.Series([8,9],index=['f','g']))
    assert eq(md.loc[:,'e'].values,[6,7,8])
    assert md.shape == (3,3)
    # print('\n',md)
    assert eq(md.mcols.loc['e'].values,[8,9])



def test_transpose():
    md,index,columns = get_data()
    md2 = md.transpose()
    assert md2.index.equals(md.columns)
    assert md2.columns.equals(md.index)
    assert eq(md2.values.T,md.values)
    md2.iloc[0,0] = 5
    assert md.iloc[0,0] == 1
    md2.index.iloc[0,0] = 100
    assert md.columns.iloc[0,0] == 5

    md2 = md.copy()
    vals = md2.values
    index = md2.index
    md2.transpose(inplace=True)
    assert md2.index.equals(md.columns)
    assert md2.columns.equals(md.index)
    assert eq(md2.values.T,md.values)
    md2.iloc[0,0] = 5
    assert vals[0,0] == 5
    md2.columns.iloc[0,0] = 100
    assert index.iloc[0,0] == 100


def test_op_call():
    md,index,columns = get_data()
    assert md != md.df

    md2 = md*2
    md3 = 2*md
    assert md2 == md3
    assert eq(md2.iloc[:,0],[2,16,16])

    md2 = md.sum(axis=0)
    assert eq(md2.values,[17,21])

    md2 = md.power(2)
    assert md2.iloc[1,0] == 64

    md.iloc[1,0] = 6
    assert md.mean().mean() == 6

    md,index,columns = get_data()
    
    md2 = md + np.array([[1,1],[1,1],[1,1]])
    assert isinstance(md,MulDataFrame)
    assert md2.iloc[0,0] == 2
    assert md2.iloc[2,1] == 11

    md2 = md + pd.DataFrame([[1,1],[1,1],[1,1]],index=['a','b','b'],
                  columns=['c','d'])
    assert isinstance(md,MulDataFrame)
    assert md2.iloc[0,0] == 2
    assert md2.iloc[2,1] == 11

    md2 = md * pd.Series([2,2],index=['c','d'])
    assert md2.iloc[0,0] == 2
    assert md2.iloc[2,1] == 20

    md2 = md * MulSeries(pd.Series([2,2],index=['c','d']))
    assert md2.iloc[0,0] == 2
    assert md2.iloc[2,1] == 20

    md2 = md.mean(axis=1)
    assert eq(md2.values,[1.5,8.5,9.0])

    def func(df):
        return df.iloc[:2]
    with pytest.raises(NotImplementedError):
        md.call(func)
    
    def func(df):
        return df.iloc[:,[1,0]]
    md2 = md.call(func)
    assert eq(md2.iloc[0].values,[2,1])
    

def test_mloc_nloc():
    md,index,columns = get_data()
    md2 = md.mloc[[..., 6]]
    # print('\n',md.mloc[[None,6],[5]])
    assert eq(md2.values,[[8,9],[8,10]])
    md2 = md.mloc[[[1,3],6]]
    assert eq(md2.values,[8,9])

    # md.index.insert(2,'z',[1,2,3])
    # md.index.columns = ['x','y','y']
    # print('xxxxxxxxxxxx')
    # print('\n',md.mloc[{'y':2}])
    # print('\n',md.mloc[{'y':2}].name)
    md,index,columns = get_data()

    md2 = md.nloc[[..., 6]]
    assert eq(md2.values,[[8,9],[8,10]])
    md2 = md.nloc[{1:6}]
    assert eq(md2.values,[[8,9],[8,10]])


    md2 = md.mloc[[[1,3],[6]]]
    assert eq(md2.values,[[8,9]])

    md2 = md.mloc[[3,6]]
    assert eq(md2.values,[8,9])

    with pytest.raises(KeyError):
        md.mloc[[1,6]]

    md2 = md.mloc[{'y':6,'x':3}]
    assert eq(md2.values,[8,9])
    md2 = md.mloc[{'y':6,'x':[3]}]
    assert eq(md2.values,[[8,9]])
    with pytest.raises(KeyError):
        md.mloc[{'y':6,'x':[1,3]}]

    md2 = md.mloc[:,[...,7]]
    assert eq(md2.values,[1,8,8])
    md2 = md.mloc[[...,6],[...,7]]
    assert eq(md2.values,[8,8])

    md2 = md.nloc[{1:6},{1:7}]
    assert eq(md2.values,[8,8])

    md2 = md.mloc[[...,2],{'g':6}]
    # print('\n',md.mloc[:,{'g':6}])
    assert md2 == 2

    md.mloc[[...,2],{'g':6}] = 3
    assert md.iloc[0,1] == 3

    md.mloc[[...,6],{'f':5}] = [5,5]
    assert eq(md.iloc[1:,0].values, [5,5])

    md.mcols.iloc[:,0] = [5,5]
    md.mloc[[1],[5]] = [3,3]
    assert eq(md.iloc[0,:].values, [3,3])

def test_set_index():
    md,index,columns = get_data()
    md2 = md.set_index('c')
    # print('\n', md.set_index(mloc={'g':6}))
    assert md2.shape == (3,1)
    assert md2.mindex.shape == (3,3)
    assert eq(md2.mindex['c'], [1,8,8])

    md.set_index('c',inplace=True,drop=False)
    assert md.shape == (3,2)
    assert md.mindex.shape == (3,3)
    assert eq(md.mindex['c'], [1,8,8])

    md,index,columns = get_data()
    md.set_index('c',inplace=True,drop=True)
    assert md.shape == (3,1)
    assert md.mindex.shape == (3,3)
    assert eq(md.mindex['c'], [1,8,8])

    md,index,columns = get_data()
    md.mcols.iloc[:,0] = [5,5]
    md2 = md.set_index(mloc=[5])
    # print(md2)
    assert md2.shape == (3,0)
    assert md2.mindex.shape == (3,4)
    assert eq(md2.mindex['c'], [1,8,8])

    with pytest.raises(ValueError):
        md.set_index()


def test_reset_index():
    md,index,columns = get_data()
    md2 = md.reset_index()
    # print(md2)
    assert md2.mindex.shape == md.mindex.shape
    assert eq(md2.mindex.index.values,[0,1,2])
    assert eq(md2.mcols.index, ['primary_index','c','d'])
    assert eq(md2.mcols.iloc[0],['',''])
    assert md2.mcols.shape == (3,2)

    md.reset_index(inplace=True,col_fill=0)
    md2 = md
    assert md2.mindex.shape == md.mindex.shape
    assert eq(md2.mindex.index.values,[0,1,2])
    assert eq(md2.mcols.index, ['primary_index','c','d'])
    assert eq(md2.mcols.iloc[0],[0,0])
    assert md2.mcols.shape == (3,2)

    md,index,columns = get_data()
    md2 = md.reset_index(drop=True)
    assert md.mindex.shape == md2.mindex.shape
    assert md.shape == md2.shape
    assert eq(md2.index.index,[0,1,2])

    md2 = md.reset_index(['x','y'])
    # print(md,'\n',md2)
    assert md2.mindex.shape == (3,0)
    assert md2.mcols.shape == (4,2)
    assert md2.mindex.index.equals(md.mindex.index)

    md2 = md.set_index('c')
    ss = md.mcols.loc['c']
    md3 = md2.reset_index('c',col_fill=ss)
    assert md3 == md
    
    md2 = md.set_index(['c','d'])
    # print(md2)
    md3 = md2.reset_index(['c','d'],col_fill=md.mcols)
    assert md3 == md

    md3 = md2.reset_index(['c','d'],col_fill=md.mcols.loc[['d','c']])
    assert md3 == md

    with pytest.raises(IndexError):
        md2.reset_index(['c','d'],col_fill=md.mcols.loc[['d','c','c']])
    md.mcols.index = ['k','m']
    with pytest.raises(KeyError):
        md2.reset_index(['c','d'],col_fill=md.mcols)


def test_drop_duplicates():
    md,index,columns = get_data()
    md2 = md.drop_duplicates('c')
    assert eq(md2.values,[[1,2],[8,9]])

    md2 = md.drop_duplicates(['c','d'])
    assert md2.equals(md)

    md2 = md.drop_duplicates(mloc=[3])
    assert md2.equals(md)

    md2 = md.drop_duplicates(mloc={'g':7})
    assert eq(md2.values,[[1,2],[8,9]])
    # print('\n',md2)

    md.drop_duplicates('c',inplace=True)
    assert eq(md.values,[[1,2],[8,9]])

    md,index,columns = get_data()
    md2 = md.drop_duplicates()
    assert md2.equals(md)
    md.iloc[1,1] = 8
    md.iloc[2,1] = 8
    md2 = md.drop_duplicates()
    assert md2.shape == (2,2)
    assert eq(md2.values,[[1,2],[8,8]])
    

def test_iterrows():
    md,index,columns = get_data()
    for i, (k,row) in enumerate(md.iterrows()):
        # print('=============')
        # print(k,'\n',row)
        assert isinstance(row,MulSeries)
        if i == 0:
            assert k.name == 'a'
        else:
            assert k.name == 'b'


def test_iloc():
    md, index, columns = get_data()
    md2 = md.iloc[np.array([0])]
    assert eq(md2.values,[[1,2]])

def test_groupby():
    md, index, columns = get_data()
    # print('\n',md.groupby('y').mean(axis=0))
    # for key, group in md.groupby('y'):
    #     if key == 6:
    #         print(key,'\n',group)
        # break
    gpo =  md.groupby('y')
    for i, (k,gp) in enumerate(gpo):
        if i==0:
            assert k == 2
            assert gp.shape == (1,2)
            assert isinstance(gp,MulDataFrame)
        else:
            assert k == 6
            assert gp.shape == (2,2)
            assert gp.mcols.shape == (2,2)
    
    md2 = md.groupby('y').mean(axis=0)
    assert eq(md2.values,[[1,2],[8,9.5]])
    assert md2.mcols.shape == (2,2)
    assert md2.index.shape == (2,0)

    md2 = md.transpose()
    md3 = md2.groupby('y',axis=1).mean(axis=1)
    assert eq(md3.columns.index.values,[2,6])
    assert eq(md3.values,[[1,8],[2,9.5]])
    assert md3.index.shape == (2,2)

    md2 = md.groupby().mean(axis=0)
    assert eq(md2.values,[[1,2],[8,9.5]])
    assert md2.index.shape == (2,1)

    md2 = md.groupby(agg_mode='list').mean(axis=0)
    assert eq(md2.values,[[1,2],[8,9.5]])
    assert md2.index.shape == (2,2)
    # print('tttttt','\n',md)
    # print('\n',md2)
    assert eq(md2.index.iloc[1,0],[3,5])

    md2 = md.groupby(['x','y']).mean(axis=0)
    assert eq(md2.values,md.values)
    assert md2.index.shape == (3,2)
    assert eq(md2.index.index.values,[0,1,2])

    md2 = md.groupby(['x','y']).mean(axis=None)
    assert eq(md2.values,[1.5,8.5,9.0])
    assert md2.shape == (3,)
    assert md2.name.name == 'mean'

    # print('\n',md)
    mf2 = md.groupby('y').sum(axis=1)
    # print('\n',mf2)
    assert mf2.shape == (3,1)
    # print(mf2.columns.shape)
    assert mf2.columns.shape == (1,0)
    assert eq(mf2.columns.index.values, ['sum'])
    assert eq(mf2.values,[[3],[17],[18]])
    assert mf2.pindex.name == 'y'

    mf2 = md.groupby('f',axis=1).sum(axis=0)
    # print('\n',mf2)
    assert mf2.shape == (1,2)
    assert eq(mf2.values, [[21,17]])
    assert eq(mf2.pindex.values, ['sum'])
    





def test_query():
    index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
    columns = pd.DataFrame([[5,7],[3,6]],
                        index=['c','d'],
                        columns=['f','g'])
    md = MulDataFrame([[1,2],[8,9],[8,10]],index=index,
                    columns=columns)
    
    md2 = md.query('c == 8')
    assert md2.shape == (2,2)
    assert md2.iloc[0,0] == 8
    # print('\n',md2)

    md3 = md.query(index='y > 3')
    assert md3 == md2

    md4 = md.query(index='y > 3',
                   columns='f>3')
    assert md4.shape == (2,1)
    assert eq(md4.values,[[8],[8]])
    assert eq(md4.mindex.values,[[3,6],[5,6]])

    md5 = md.query('c==8',index='x<=3')
    assert md5.shape == (1,2)
    assert eq(md5.values,[[8,9]])

    md6 = md.query('c==8',index='x<=3',
                   columns='f>3')
    assert md6.shape == (1,1)
    assert eq(md6.values,[[8]])
    assert md6.mcols.shape == (1,2)
    # print('\n',md6)

    md7 = md.copy()
    md7.query('c==8',index='x<=3',
                   columns='f>3',
                   inplace=True)
    assert md6 == md7

    md8 = md.query(columns='g < 7')
    assert md8.shape == (3,1)




def test_melt():
    index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
    columns = pd.DataFrame([[5,7],[3,6]],
                        index=['c','d'],
                        columns=['f','g'])
    md = MulDataFrame([[1,2],[8,9],[8,10]],index=index,
                    columns=columns)
    
    mf = md.melt()
    # print(mf)
    # print(mf)
    assert mf.shape == (md.shape[0]*md.shape[1],7)
    assert eq(mf['value'].values,np.ravel(md.values))
    assert eq(mf.columns.tolist(),
              ['index','x','y','index','f','g','value'])
    
    mf2 = md.melt(prefix=True,value_name='num')
    assert mf2.shape == (md.shape[0]*md.shape[1],7)
    assert mf2.columns[-1] == 'num'
    assert mf2.columns[0] == 'x_index'
    assert eq(mf2['x_index'].values,
              ['a','a','b','b','b','b'])
    assert eq(mf2['y_index'].values,
              ['c','d','c','d','c','d'])
    
    md.mcols.columns = ['x','g']
    def prefix_func(indexType,label):
        if indexType == 'index':
            label = f'row_{label}'
        else:
            label = f'col_{label}'
        return label
    
    mf3 = md.melt(prefix=prefix_func,
                  ignore_primary_columns=True,
                  ignore_primary_index=True)
    assert mf3.shape == (md.shape[0]*md.shape[1],5)
    assert eq(mf3.columns.tolist(),
              ['row_x','y','col_x','g','value'])


def test_sort_values():
    index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','b'],
                     columns=['x','y'])
    columns = pd.DataFrame([[5,7],[3,6]],
                        index=['c','d'],
                        columns=['f','g'])
    mf = MulDataFrame([[1,9],[8,2],[7,10]],index=index,
                    columns=columns)
    
    mf2 = mf.sort_values('d')
    assert eq(mf2.pindex, ['b','a','b'])
    assert eq(mf2.values[:,1],[2,9,10])

    
    index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','c'],
                     columns=['x','y'])
    mf.index = index
    mf2 = mf.sort_values('c')
    assert eq(mf2.pindex, ['a','c','b'])
    assert eq(mf2.values[:,0], [1,7,8])

    mf2 = mf.sort_values('b',axis=1)
    # print('\n',mf2)
    assert eq(mf2.pcols, ['d','c'])
    assert eq(mf2.values[1], [2,8])

    mf.pcols = ['d','d']
    mf2 = mf.sort_values('b',axis=1)
    # print('\n',mf2)
    assert eq(mf2.pcols, ['d','d'])
    assert eq(mf2.values[1], [2,8])



    # print('\n',mf2)
    