import copy
import math

import numpy as np
import pandas as pd
from utils.check_utils import (check_gen, find_low_high_irv, find_low_high_oc,
                               get_roc_check_by_tag)

from configs.constants import BUCKET, CHECK_PERIOD, ORG
from configs.influx_client import write_api


def overange_check(df: pd.DataFrame, tags: list = [], pivot: bool = False) -> pd.DataFrame:
    if df is None or df.empty or len(tags) == 0:
        return
    res = copy.deepcopy(df)
    if pivot:
        for tag in tags:
            if tag in df.columns:
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
            if tag in df.columns:
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


def roc_check(table: pd.DataFrame, devices):
    res = copy.deepcopy(table)
    roc_checks_with_data = []
    for col in table.columns:
        max, min = find_low_high_oc(table[col].values)
        numerator = 2 * (max - min)
        denominator = (max + min) * (60 * CHECK_PERIOD * 2)
        if denominator == 0:
            res[col] = 0
        else:
            rroc = abs(numerator / denominator)
        roc_check_type = get_roc_check_by_tag(col, devices)
        if roc_check_type == "Pressure":
            if rroc > 0.05:
                roc_checks_with_data.append({"measurement": "roc_checks", "fields": {col: 1}, "tags": {"tag": col, "type": "Pressure"}, "time": table.index[-1]})
        elif roc_check_type == "Temperature":
            if rroc > 0.1:
                roc_checks_with_data.append({"measurement": "roc_checks", "fields": {col: 1}, "tags": {"tag": col, "type": "Temperature"}, "time": table.index[-1]})
        elif roc_check_type == "Validation":
            if rroc > 0.2:
                roc_checks_with_data.append({"measurement": "roc_checks", "fields": {col: 1}, "tags": {"tag": col, "type": "Validation"}, "time": table.index[-1]})
    return roc_checks_with_data


def deviation_check(table, deviation_checks):
    deviation_checks_with_data = []
    for key, tags in deviation_checks.items():
        if len(tags) == 2:
            if pd.Series(tags).isin(table.columns).all():
                values = table[tags[0]] - table[tags[1]]
                for value in values:
                    _tags = {}
                    for idx, tag in enumerate(tags):
                        _tags[f"tag_{idx}"] = tag
                    deviation_checks_with_data.append({"measurement": "deviation_checks", "fields": {key: value}, "tags": _tags})
    return deviation_checks_with_data


def do_roc_check(table, devices):
    roc_checks = roc_check(table, devices)
    for point in roc_checks:
        write_api.write(bucket=BUCKET, record=point, org=ORG)
    # print("write roc_check done")


def do_deviation_check(table, deviation_checks_detail):
    deviation_checks = deviation_check(table, deviation_checks_detail)
    for point in deviation_checks:
        write_api.write(bucket=BUCKET, record=point, org=ORG)
        print("write dev_check done")


def do_irv_check(table, tags):
    irv_checks = irv_check(table, tags, True)
    for point in check_gen("irv_check", irv_checks):
        write_api.write(bucket=BUCKET, record=point, org=ORG)
        print("write irv_check done")


def do_overange_check(table, tags):
    overange_checks = overange_check(table, tags, True)
    for point in check_gen("overange_check", overange_checks):
        write_api.write(bucket=BUCKET, record=point, org=ORG)
        print("write overange_check done")


def do_nan_check(table, tags):
    nan_checks = nan_check(table, tags, True)
    for point in check_gen("nan_check", nan_checks):
        write_api.write(bucket=BUCKET, record=point, org=ORG)
        print("write nan done")
