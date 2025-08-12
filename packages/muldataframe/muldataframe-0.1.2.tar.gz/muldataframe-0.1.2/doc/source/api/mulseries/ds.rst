MulSeries.ds
=================

.. currentmodule:: muldataframe

.. attribute:: MulSeries.ds

      A partial copy of the values series. 

      It is different from the :doc:`MulSeries.ss <ss>` in that its values are not copied but refer to the values of the values series while its index and name are deep-copied from the values series. Use this attribute if you want to save some memory or use the same name to refer to the values series/dataframe of MulSeries/MulDataFrame.
      