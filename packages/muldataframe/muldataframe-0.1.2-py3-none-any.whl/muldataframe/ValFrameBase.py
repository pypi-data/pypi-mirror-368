import pandas as pd
import muldataframe.cmm as cmm
import warnings

def ValFrameBase_factory(baseClass:pd.DataFrame|pd.Series):
    class ValFrameBase(baseClass):
        def __init__(self,parent,df):
            super().__init__(df)
            # if baseClass == pd.DataFrame:
            #     print(df.shape,self.shape)
            # self.parent = parent
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.__parent = parent
            # if baseClass == pd.DataFrame:
            #     print(df.shape,self.shape)

        # @abstractmethod
        def _update_super_index(self):
            self.index = self.__parent.mindex.index
            if hasattr(self,'columns'):
                self.columns = self.__parent.mcolumns.index
            if hasattr(self,'name'):
                self.name = self.__parent.name.name

        def __getitem__(self,key):
            # # Without calling self._update_super_index(),
            # # the expression below uses self.parent.mindex.index
            # # to index but returns a dataframe or series with
            # # super(ValDataFrame,self).index.
            # res = super().__getitem__(key)
            self._update_super_index()
            return super().__getitem__(key)
        
        def __setitem__(self,key,val):
            self._update_super_index()
            return super().__setitem__(key,val)
            
        # def __getattr__(self,name):
        #     if name == 'parent':
        #         return self.__parent

        def __getattribute__(self, name:str):
            if name == 'index':
                return super().__getattribute__('__parent').mindex.index
            elif name == 'columns':
                return super().__getattribute__('__parent').mcolumns.index
            elif name == 'name':
                return super().__getattribute__('__parent').name.name
            elif name == 'iloc':
                # self._update_super_index()
                return super().__getattribute__('iloc')
            elif name == 'loc':
                
                # print(self,super().__getattribute__('columns'))
                super().__getattribute__('_update_super_index')()
                # self._update_super_index()
                return super().__getattribute__('loc')
            else:
                return super().__getattribute__(name)
    return ValFrameBase