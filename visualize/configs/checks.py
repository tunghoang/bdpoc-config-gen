import copy
import math

import numpy as np
import pandas as pd
from utils.check_utils import (find_low_high_irv, find_low_high_oc_by_devices, get_frozen_check_roc_check_by_tag, get_roc_check_by_tag)

from configs.constants import (AVAILABLE_DEVIATION, CHECK_PERIOD, MINIMUM_RATIO_NAN_ALLOW, SECOND)


def overange_check(df: pd.DataFrame, devices: list, tags: list = [], pivot: bool = False) -> pd.DataFrame:
  if df is None or df.empty or len(tags) == 0:
    return
  res = copy.deepcopy(df)
  if pivot:
    for tag in tags:
      if tag in df.columns:
        max, min = find_low_high_oc_by_devices(devices, tag)
        if max and min:
          res[tag] = [np.nan if math.isnan(value) else 1 if value >= max else 0 if value < max and value > min else -1 for value in res[tag].values]
    return res
  for tag in tags:
    max, min = find_low_high_oc_by_devices(devices, tag)
    if max and min:
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
  nan_check_with_data = []
  if pivot:
    for tag in tags:
      if (tag in res.columns):
        count_nan = res[tag].isnull().sum()
        count_total = len(res.index)
        if count_nan / count_total > MINIMUM_RATIO_NAN_ALLOW:
          nan_check_with_data.append({"measurement": "nan_check", "fields": {tag: 1}, "tags": {"tag": tag}, "time": res.index[-1]})
          # res[tag] = [1 if math.isnan(row[tag]) else 0 for _, row in df.iterrows()]
    return nan_check_with_data
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
          row["_value"] if row["_field"] != tag else np.nan if math.isnan(row["_value"]) else 3 if row["_value"] >= max3 else
          2 if row["_value"] >= max2 and row["_value"] < max3 else 1 if row["_value"] >= max1 and row["_value"] < max2 else 0 if row["_value"] >= min1 and row["_value"] < max1 else -1 if row["_value"] >= min2 and row["_value"] < min1 else -2 if row["_value"] >= min3 and row["_value"] < min2 else -3
          for _, row in res.iterrows()
      ]
  return res


def deviation_check(table: pd.DataFrame, deviation_checks: dict, devices: list):
  deviation_checks_with_data = []
  for key, tags in deviation_checks.items():
    # CHECK IF DEVIATION CHECK AVAILABLE
    if len(tags) == AVAILABLE_DEVIATION and pd.Series(tags).isin(table.columns).all():
      max, min = find_low_high_oc_by_devices(devices, tags[0])
      if max and min:
        values = abs(table[tags[0]] - table[tags[1]]) / (max - min)
        for value in values:
          if value > 0.05:
            _tags = {}
            for idx, tag in enumerate(tags):
              _tags[f"tag_{idx}"] = tag
            deviation_checks_with_data.append({"measurement": "deviation_checks", "fields": {key: value}, "tags": _tags})
  return deviation_checks_with_data


def roc_check(table: pd.DataFrame, devices):
  res = copy.deepcopy(table)
  roc_checks_with_data = []
  for col in table.columns:
    max, min = find_low_high_oc_by_devices(devices, col)
    if max and min:
      numerator = 2 * (max - min)
      denominator = (max + min) * (SECOND * CHECK_PERIOD * 2)
      if denominator == 0:
        res[col] = 0
      else:
        rroc = abs(numerator / denominator)
      if rroc > 0.05:
        roc_checks_with_data.append({"measurement": "roc_check", "fields": {col: 1}, "tags": {"tag": col, "type": "Pressure"}, "time": table.index[-1]})
  return roc_checks_with_data


def frozen_check(table: pd.DataFrame, devices):
  res = copy.deepcopy(table)
  frozen_checks_with_data = []
  for col in table.columns:
    max, min = find_low_high_oc_by_devices(devices, col)
    if max and min:
      numerator = 2 * (max - min)
      denominator = (max + min) * (60 * CHECK_PERIOD * 2)
      if denominator == 0:
        res[col] = 0
      else:
        rroc = abs(numerator / denominator)
      _, is_frozen_check = get_frozen_check_roc_check_by_tag(col, devices)
      if is_frozen_check:
        if rroc < 0.05:
          frozen_checks_with_data.append({"measurement": "frozen_check", "fields": {col: 1}, "tags": {"tag": col, "type": "Pressure"}, "time": table.index[-1]})
  return frozen_checks_with_data
