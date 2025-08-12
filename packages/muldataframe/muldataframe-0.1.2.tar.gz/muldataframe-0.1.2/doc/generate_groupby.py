from lib import *


attrs = ['parent','by',
         'index_agg','indexType','groupBy']

methods = ['__iter__','call']

fld = 'source/api/groupby'

generate_attr_files('MulGroupBy',
    attrs,{},'source/api/groupby',
    'cmm.MulGroupBy')

generate_method_files('MulGroupBy',
    methods,'source/api/groupby',
    'cmm.MulGroupBy')

data = [['Constructor',['mulgroupby']],
        ['Attributes',attrs],
        ['Methods',methods]]
desc = 'The class for the object returned by the :doc:`MulSeries.groupby <../mulseries/groupby>` or the :doc:`MulDataFrame.groupby,<../muldataframe/groupby>` method.'
generate_index('MulGroupBy',data,f'{fld}/indices.rst',desc)