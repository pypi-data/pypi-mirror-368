from lib import *


ss_attrs_only = ['index','name',
         'values','ss','ds','shape',
         'primary_index','primary_name',
         'mindex','mname','pindex','pname']
ss_indexing = ['iloc','loc','mloc','nloc']

ss_attrs = ss_attrs_only+ss_indexing

# def get_lex(num):
#    # print(num)
#    fold = int(num/9)
#    residue = num%9
#    # print(fold,residue)
#    if fold > 9:
#       return get_lex(fold)+str(residue)
#    else:
#       return str(fold)+str(residue)

# mp={}
# fnames = ['00_mulseries.rst']
# for i, ax in enumerate(ss_attrs):
#    lex = get_lex(i+1)
#    fname = f'{lex}_{ax}.rst'
#    fnames.append(fname)
#    mp[ax] = fname.split('.')[0]

ss_dyn_attrs = {
   'values':
      '''
      The values of the values series. 
      
      It is not a copy.
      ''',
   'ss':
      '''
      A deep copy of the values series.
      ''',
   'ds':
      '''
      A partial copy of the values series. 

      It is different from the :doc:`MulSeries.ss <ss>` in that its values are not copied but refer to the values of the values series while its index and name are deep-copied from the values series. Use this attribute if you want to save some memory or use the same name to refer to the values series/dataframe of MulSeries/MulDataFrame.
      ''',
   'shape':
      '''
      Same as the shape of the values series.
      ''',
   'mindex':
      '''
      Alias for :doc:`MulSeries.index <index>`.
      ''',
   'mname':
      '''
      Alias for :doc:`MulSeries.name <name>`.
      ''',
   'primary_index':
      '''
      The primary index.
      
      Shorthand for ``MulSeries.index.index``.
      ''',
   'pindex':
      '''
      Alias for :doc:`MulSeries.primary_index <primary_index>`.
      ''',
   'primary_name':
      '''
      The primary name.
      
      Shorthand for ``MulSeries.name.name``.
      ''',
   'pname':
      '''
      Alias for :doc:`MulSeries.primary_name <primary_name>`.
      ''',
   
}

fnames = []
for ax in ss_attrs:
   fname = ax+'.rst'
   fnames.append(fname)
   # print(i,lex,fname)
   
   with open(f'source/api/mulseries/{fname}','w') as ff:
      underlines = '='*(len(ax)+15)
      ff.write(f'MulSeries.{ax}\n{underlines}\n\n')
      if ax not in ss_dyn_attrs:
         ff.write(f'.. autoattribute:: muldataframe.MulSeries.{ax}\n')
      else:
         ff.write('.. currentmodule:: muldataframe\n\n')
         ff.write(f'.. attribute:: MulSeries.{ax}\n')
         ff.write(ss_dyn_attrs[ax])


methods = ['__iter__','copy','equals','reset_index','query','sort_values','drop_duplicates','call','groupby','insert','drop']
method_fnames = []
for ax in methods:
   fname = ax+'.rst'
   method_fnames.append(fname)
   # print(i,lex,fname)
   
   with open(f'source/api/mulseries/{fname}','w') as ff:
      underlines = '='*(len(ax)+15)
      ff.write(f'MulSeries.{ax}\n{underlines}\n\n')
      if ax not in ss_dyn_attrs:
         ff.write(f'.. automethod:: muldataframe.MulSeries.{ax}\n')
      else:
         pass
         # ff.write('.. currentmodule:: muldataframe\n\n')
         # ff.write(f'.. attribute:: MulSeries.{ax}\n')
         # ff.write(ss_dyn_attrs[ax])


data = [['Constructor',['mulseries']],
        ['Attributes',ss_attrs_only],
        ['indexing',ss_indexing],
        ['Methods',methods]] 
generate_index('MulSeries',data,f'source/api/mulseries//indices.rst')
# with open('source/__template/index.rst','r') as rf:
#    wstr = rf.read()
#    wstr.replace('{title}','MulSeries')

#    lines = '\n'.join([f'   {x}' for x in ss_attrs_only])
#    wstr = wstr.replace('{attributes}',lines)

#    lines = '\n'.join([f'   {x}' for x in ss_indexing])
#    wstr = wstr.replace('{indexing}',lines)

#    mlines = '\n'.join([f'   {x}' for x in methods])
#    wstr = wstr.replace('{methods}',mlines)
#    with open(f'source/api/mulseries/indices.rst','w') as wf:
#       wf.write(wstr)

# # print(ss_dyn_attrs)