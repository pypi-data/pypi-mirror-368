

def generate_attr_files(title, attrs:list[str],
    dyn_attrs:dict,fld,module=None):
    if module is None:
        module = title
    for ax in attrs:
        fname = ax+'.rst'
        with open(f'{fld}/{fname}','w') as ff:
            underlines = '='*(len(ax)+15)
            ff.write(f'{title}.{ax}\n{underlines}\n\n')
            if ax not in dyn_attrs:
                ff.write(f'.. autoattribute:: muldataframe.{module}.{ax}\n')
            else:
                ff.write('.. currentmodule:: muldataframe\n\n')
                ff.write(f'.. attribute:: {module}.{ax}\n')
                ff.write(dyn_attrs[ax])

def generate_method_files(title,methods:list[str],
                          fld,module=None):
    if module is None:
        module = title

    for ax in methods:
        fname = ax+'.rst'
        with open(f'{fld}/{fname}','w') as ff:
            underlines = '='*(len(ax)+15)
            ff.write(f'{title}.{ax}\n{underlines}\n\n')
            ff.write(f'.. automethod:: muldataframe.{module}.{ax}\n')

def generate_index(title,data,path,desc=None):
    with open(path,'w') as ff:
        underlines = '='*(len(title)+15)
        ff.write(f'{title}\n{underlines}\n\n')
        if desc:
            ff.write(f'{desc}\n\n')
        for item in data:
            desc = item[0]
            print(desc)
            lines = '\n'.join([f'   {x}' for x in item[1]])
            ff.write(f'.. toctree::\n   :maxdepth: 1\n   :caption: {desc}:\n\n')
            ff.write(lines+'\n\n')