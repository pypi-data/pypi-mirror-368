numpy functions
=================
Similar to MulSeries and MulDataFrame (see :doc:`../../user_guide/numpy_functions` user guide), all numpy functions in the main namespace have been added to MulGroupBy as methods using the :doc:`MulGroupBy.call <call>` method. But there three major differences between the numpy functions added to MulGroupBy and those added to MulSeries or MulDataFrame.

First, no pandas methods are added to MulGroupBy. Users do not need to worry abount wether a method is called using a pandas method or a numpy function.

Second, the numpy methods of MulGroupBy have an implicit axis parameter that is the same as the axis parameter in the groupby method. For example, ``mf.groupby(axis=1).sum()`` implies that the numpy ``sum`` function is called on the values dataframe with ``axis=1`` in each group. You can overwrite this behavior by explicitly assigning the axis parameter ``mf.groupby(axis=1).sum(axis=0)``, though it is rarely needed to do so.

Third, the numpy methods have two more keyword arguments ``use_mul`` and ``set_primary`` than the original numpy functions. You can learn more about these two keyword arguments in :doc:`call`. 
