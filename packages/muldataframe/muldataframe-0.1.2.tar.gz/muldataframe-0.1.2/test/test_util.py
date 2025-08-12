# from ..MulDataFrame import MulDataFrame
# from ..MulSeries import MulSeries
# from ..util import pivot_table,concat
import pandas as pd
from .lib import eq
import muldataframe as md
MulDataFrame = md.MulDataFrame
MulSeries = md.MulSeries
from muldataframe.util import pivot_table,concat


def test_pivot_table():
    df = pd.DataFrame({"A": ["foo", "foo", "foo", "foo", "foo",
                         "bar", "bar", "bar", "bar"],
                   "B": ["one", "one", "one", "two", "two",
                         "one", "one", "two", "two"],
                   "C": ["small", "large", "large", "small",
                         "small", "large", "small", "small",
                         "large"],
                   "D": [1, 2, 2, 3, 3, 4, 5, 6, 7],
                   "E": [2, 4, 5, 5, 6, 6, 8, 9, 9]})
    
    table = pivot_table(df, values='D', index=['A', 'B'],
            columns=['C'], aggfunc="sum")
    # print('\n',table)
    assert table.index.equals(pd.DataFrame(
        [['bar','one'],['bar','two'],
         ['foo','one'],['foo','two']],
         columns=['A','B']
    ))
    assert table.columns.shape == (2,0)
    assert eq(table.columns.index,['large','small'])

def test_concat():
    index = pd.DataFrame([[1,2],[3,6],[5,6]],
                     index=['a','b','c'],
                     columns=['x','y'])
    columns = pd.DataFrame([[5,7],[3,6]],
                        index=['c','d'],
                        columns=['f','g'])
    mf = MulDataFrame([[1,2],[8,9],[8,10]],index=index, columns=columns)
    ms = MulSeries([5,6,7],index=pd.DataFrame(index=['a','b','c']),name=pd.Series([8,9],index=['g','f'],name='k'))
#     print('\n',mf)
#     print('\n',ms)
    mf2 = concat([mf,ms],axis=1)
    mf3 = concat([ms,mf],axis=1)
    assert (mf2.mindex.shape == (3,2))
    assert (mf3.mindex.shape == (3,0))
    assert (mf2.shape == (3,3))
    assert eq(mf2.columns.values, [[5,7],[3,6],[9,8]])
    assert eq(mf3.columns.values, [[8,9],[7,5],[6,3]])
