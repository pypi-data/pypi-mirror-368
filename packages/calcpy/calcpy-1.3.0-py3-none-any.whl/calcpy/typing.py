from collections import UserDict, UserList, UserString

import numpy as np
import pandas as pd

DictTypes = (dict, UserDict)
ListTypes = (list, UserList)
StrTypes = (str, UserString)
StrLike = StrTypes + (bytes, bytearray)
ListLike = ListTypes + (tuple, set)
StrListLike = StrLike + ListLike
NDFrame = (pd.Series, pd.DataFrame)
Broadcastable = (np.ndarray,) + NDFrame
Uniquable = StrListLike + Broadcastable
