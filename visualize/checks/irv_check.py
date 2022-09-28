import copy
import math
import warnings
import pandas as pd
import numpy as np

def find_low_high_irv(col):
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

def irv_check(df, tags=[], pivot=False):
    if df is None or df.empty or len(tags) == 0:
        return
    res = copy.deepcopy(df)
    if pivot:
        for tag in tags:
            max3, max2, max1, min1, min2, min3 = find_low_high_irv(df[tag].values)
            # print(max3, max2, max1, min1, min2, min3)
            res[tag] = [
                np.nan if math.isnan(value) else 3 if value >= max3 else 2 if value >= max2 and value < max3 else 1 if value >= max1 and value < max2 else 0 if value >= min1 and value < max1 else -1 if value >= min2 and value < min1 else -2 if value >= min3 and value < min2 else -3
                for value in res[tag].values
            ]
        return res
    for tag in tags:
        max3, max2, max1, min1, min2, min3 = find_low_high_irv(df[df["_field"] == tag]["_value"].values)
        # print(max3, max2, max1, min1, min2, min3)
        res["_value"] = [
            row["_value"] if row["_field"] != tag else np.nan if math.isnan(row["_value"]) else 3 if row["_value"] >= max3 else 2
            if row["_value"] >= max2 and row["_value"] < max3 else 1 if row["_value"] >= max1 and row["_value"] < max2 else 0 if row["_value"] >= min1 and row["_value"] < max1 else -1 if row["_value"] >= min2 and row["_value"] < min1 else -2 if row["_value"] >= min3 and row["_value"] < min2 else -3
            for _, row in res.iterrows()
        ]
    return res