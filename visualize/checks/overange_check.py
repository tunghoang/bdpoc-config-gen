import copy
import math
import warnings
import pandas as pd
import numpy as np

def find_low_high_oc(col):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        max = np.nanmax(col)
        min = np.nanmin(col)
        return max, min

def overange_check(df, tags=[], pivot=False):
    if df is None or df.empty or len(tags) == 0:
        return
    res = copy.deepcopy(df)
    if pivot:
        for tag in tags:
            max, min = find_low_high_oc(df[tag].values)
            res[tag] = [np.nan if math.isnan(value) else 1 if value >= max else 0 if value < max and value > min else -1 for value in res[tag].values]
        return res
    for tag in tags:
        max, min = find_low_high_oc(df[df["_field"] == tag]["_value"].values)
        # SHORTHAND version
        res["_value"] = [np.nan if math.isnan(row["_value"]) else 1 if row["_value"] >= max else 0 if row["_value"] < max and row["_value"] > min else -1 for _, row in res.iterrows()]
        # EASY TO READ version
        # for index, row in df.iterrows():
        #     if (row["_field"] == tag):
        #         if (math.isnan(row["_value"])):
        #             continue
        #         elif (row["_value"] >= max):
        #             df["_value"][index] = 1
        #         elif (row["_value"] < max and row["_value"] > min):
        #             df["_value"][index] = 0
        #         elif (row["_value"] <= min):
        #             df["_value"][index] = -1
    return res