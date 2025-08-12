from lib import *

fld = 'source/api/muldataframe'
name = 'MulDataFrame'


attrs_only = ['index','columns',
         'values','df','ds','shape',
         'primary_index', 'primary_columns',
         'mindex','mcolumns','mcols','pindex','pcolumns','pcols']
attrs_indexing = ['iloc','loc','mloc','nloc']

dyn_attrs = {
   'values':
      '''
      The values of the values dataframe.
    
      It is not a copy.
      ''',
   'df':
      '''
      A deep copy of the values dataframe.
      ''',
   'ds':
      '''
      A partial copy of the values dataframe. 

      It is different from the :doc:`MulDataFrame.df <df>` in that its values are not copied but refer to the values of the values dataframe while its index and columns are deep-copied from the values dataframe. Use this attribute if you want to save some memory or use the same name to refer to the values series/dataframe of MulSeries/MulDataFrame.
      ''',
   'shape':
      '''
      Same as the shape of the values dataframe.
      ''',
   'mindex':
      '''
      Alias for :doc:`MulDataFrame.index <index>`.
      ''',
   'mcolumns':
      '''
      Alias for :doc:`MulDataFrame.columns <columns>`.
      ''',
   'mcols':
      '''
      Alias for :doc:`MulDataFrame.columns <columns>`.
      ''',
   'primary_index':
      '''
      The primary index.
      
      Shorthand for ``MulDataFrame.index.index``.
      ''',
   'pindex':
      '''
      Alias for :doc:`MulDataFrame.primary_index <primary_index>`.
      ''',
   'primary_columns':
      '''
      The primary columns.
      
      Shorthand for ``MulDataFrame.columns.index``.
      ''',
   'pcolumns':
      '''
      Alias for :doc:`MulDataFrame.primary_columns <primary_columns>`.
      ''',
   'pcols':
      '''
      Alias for :doc:`MulDataFrame.primary_columns <primary_columns>`.
      ''',
}


generate_attr_files(name,
    attrs_only+attrs_indexing,dyn_attrs,fld)


methods = ['__iter__','copy','equals','transpose',
'set_index','reset_index','query','iterrows',
'sort_values','drop_duplicates','call',
'groupby','melt',
'insert','drop']

generate_method_files(name,
    methods,fld)

data = [['Constructor',['muldataframe']],
        ['Attributes',attrs_only],
        ['Indexing',attrs_indexing],
        ['Methods',methods]]
generate_index(name,data,f'{fld}/indices.rst')