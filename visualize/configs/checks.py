import copy
import math
import numpy as np
import pandas as pd
from utils.check_utils import find_low_high_oc, find_low_high_irv

def overange_check(df: pd.DataFrame, tags: list = [], pivot: bool = False) -> pd.DataFrame:
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
        if (max and min):
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

def nan_check(df: pd.DataFrame, tags: list = [], pivot: bool = False) -> pd.DataFrame:
    if df is None or df.empty or len(tags) == 0:
        return
    res = copy.deepcopy(df)
    if pivot:
        for tag in tags:
            if (tag in res.columns):
                res[tag] = [1 if math.isnan(row[tag]) else 0 for _, row in df.iterrows()]
        return res
    res["_value"] = [1 if math.isnan(row["_value"]) else 0 for _, row in df.iterrows()]
    return res

def irv_check(df: pd.DataFrame, tags: list = [], pivot: bool = False) -> pd.DataFrame:
    if df is None or df.empty or len(tags) == 0:
        return
    res = copy.deepcopy(df)
    if pivot:
        for tag in tags:
            max3, max2, max1, min1, min2, min3 = find_low_high_irv(df[tag].values)
            res[tag] = [
                np.nan if math.isnan(value) else 3 if value >= max3 else 2 if value >= max2 and value < max3 else 1 if value >= max1 and value < max2 else 0 if value >= min1 and value < max1 else -1 if value >= min2 and value < min1 else -2 if value >= min3 and value < min2 else -3
                for value in res[tag].values
            ]
        return res
    for tag in tags:
        max3, max2, max1, min1, min2, min3 = find_low_high_irv(df[df["_field"] == tag]["_value"].values)
        if (max3 and max2 and max1 and min1 and min2 and min3):
            res["_value"] = [
                row["_value"] if row["_field"] != tag else np.nan if math.isnan(row["_value"]) else 3 if row["_value"] >= max3 else 2 if row["_value"] >= max2 and row["_value"] < max3 else
                1 if row["_value"] >= max1 and row["_value"] < max2 else 0 if row["_value"] >= min1 and row["_value"] < max1 else -1 if row["_value"] >= min2 and row["_value"] < min1 else -2 if row["_value"] >= min3 and row["_value"] < min2 else -3 for _, row in res.iterrows()
            ]
    return res