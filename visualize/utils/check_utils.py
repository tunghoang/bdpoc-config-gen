import warnings
import numpy as np
import pandas as pd

def find_low_high_oc(col: pd.Series) -> tuple:
    if col.size == 0:
        return None, None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        max = np.nanmax(col)
        min = np.nanmin(col)
        return max, min

def find_low_high_irv(col: pd.Series) -> tuple:
    if col.size == 0:
        return None, None, None, None, None, None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        col = list({value for value in col if pd.notna(value)})
        col.sort(reverse=True)
        max3 = col[0] if len(col) > 0 else 0
        max2 = col[1] if len(col) > 1 else 0
        max1 = col[2] if len(col) > 2 else 0
        min3 = col[-1] if len(col) > 3 else 0
        min2 = col[-2] if len(col) > 4 else 0
        min1 = col[-3] if len(col) > 5 else 0
        return max3, max2, max1, min1, min2, min3