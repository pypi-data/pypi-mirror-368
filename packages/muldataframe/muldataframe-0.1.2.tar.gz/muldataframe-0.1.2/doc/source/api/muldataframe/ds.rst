MulDataFrame.ds
=================

.. currentmodule:: muldataframe

.. attribute:: MulDataFrame.ds

      A partial copy of the values dataframe. 

      It is different from the :doc:`MulDataFrame.df <df>` in that its values are not copied but refer to the values of the values dataframe while its index and columns are deep-copied from the values dataframe. Use this attribute if you want to save some memory or use the same name to refer to the values series/dataframe of MulSeries/MulDataFrame.
      