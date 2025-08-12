import numpy as np
def eq(list1, list2):
    if len(list1)!= len(list2):
        return False
    for i in range(len(list1)):
        if isinstance(list1[i],list) or isinstance(list1[i],np.ndarray):
            if not eq(list1[i],list2[i]):
                return False
        else:
            if list1[i]!= list2[i]: 
                return False
    return True