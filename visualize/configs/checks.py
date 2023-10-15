import copy
import datetime as dt
import math
from typing import List

import numpy as np
import pandas as pd
import pytz
import streamlit as st
from utils.check_utils import (find_low_high_irv_by_devices, find_low_high_oc_by_devices, get_frozen_check_roc_check_by_tag)

from configs.constants import (AVAILABLE_DEVIATION, CHECK_PERIOD, DATE_NOW, DEVIATION_CHECK_VALUE, FROZEN_CHECK_VALUE, MINIMUM_RATIO_NAN_ALLOW, PIVOT, SECOND)


def overange_check(df: pd.DataFrame, devices: List[dict], tags: list = []) -> pd.DataFrame:
  if df is None or df.empty or len(tags) == 0:
    return
  res = copy.deepcopy(df)
  if PIVOT:
    for tag in df.columns:
      max, min = find_low_high_oc_by_devices(devices, tag)
      if max is not None and min is not None:
        res[tag] = [np.nan if math.isnan(value) else 1 if value >= max else 0 if value < max and value > min else -1 for value in res[tag].values]
      else:
        res.drop(columns=tag, inplace=True)
    res = res.assign(_measurement="overange_check")
    return res
  for tag in tags:
    max, min = find_low_high_oc_by_devices(devices, tag)
    if [max, min].count() == 0:
      res["_value"] = [np.nan if math.isnan(row["_value"]) else 1 if row["_value"] >= max else 0 if row["_value"] < max and row["_value"] > min else -1 for _, row in res.iterrows()]
  res = res.assign(_measurement="overange_check")
  return res
  
def nan_check(df: pd.DataFrame, tags: list = []) -> pd.DataFrame:
  if df is None or df.empty or len(tags) == 0:
    return
  res = copy.deepcopy(df)
  nan_check_with_data = pd.DataFrame()
  if PIVOT:
    for tag in res.columns:
      count_nan = res[tag].isnull().sum()
      count_total = len(res.index)
      if count_nan / count_total > MINIMUM_RATIO_NAN_ALLOW:
        nan_check_with_data = pd.concat(
          [
            pd.DataFrame(
              {
                "_measurement": "nan_check", 
                tag: 1, 
                "_time": DATE_NOW()
              }, 
              index=[ res.index[-1] ]
            ), nan_check_with_data
          ], 
          join="outer"
        )
      # Add missing tags data
      for t in tags:
        if t not in res.columns:
          nan_check_with_data = pd.concat(
            [pd.DataFrame({"_measurement": "nan_check", t: np.nan, "_time": DATE_NOW()}, index=[res.index[-1]]), nan_check_with_data], 
            join="outer"
          )
    return nan_check_with_data
  res["_value"] = [1 if math.isnan(row["_value"]) else 0 for _, row in df.iterrows()]
  return res


def irv_check(df: pd.DataFrame, devices: List[dict], tags: list = []) -> pd.DataFrame:
  if df is None or df.empty or len(tags) == 0:
    return
  res = copy.deepcopy(df)
  if PIVOT:
    for tag in res.columns:
      max3, max2, max1, min1, min2, min3 = find_low_high_irv_by_devices(devices, tag)
      if [max3, max2, max1, min1, min2, min3].count(None) == 0:
        res[tag] = [
            np.nan if math.isnan(value) else 3 if value >= max3 else 2 if value >= max2 and value < max3 else 1 if value >= max1 and value < max2 else 0 if value >= min1 and value < max1 else -1 if value >= min2 and value < min1 else -2 if value >= min3 and value < min2 else -3
            for value in res[tag].values
        ]
      else:
        res.drop(columns=tag, inplace=True)
    res = res.assign(_measurement="irv_check")
    return res
  for tag in tags:
    max3, max2, max1, min1, min2, min3 = find_low_high_irv_by_devices(devices, tag)
    if [max3, max2, max1, min1, min2, min3].count(None) == 0:
      res["_value"] = [
          row["_value"] if row["_field"] != tag else np.nan if math.isnan(row["_value"]) else 3 if row["_value"] >= max3 else
          2 if row["_value"] >= max2 and row["_value"] < max3 else 1 if row["_value"] >= max1 and row["_value"] < max2 else 0 if row["_value"] >= min1 and row["_value"] < max1 else -1 if row["_value"] >= min2 and row["_value"] < min1 else -2 if row["_value"] >= min3 and row["_value"] < min2 else -3
          for _, row in res.iterrows()
      ]
  return res


def deviation_check(table: pd.DataFrame, deviation_checks: dict, devices: List[dict], tagDict):
  points = []
  if table.empty:
    return points
  print(table.columns)
  checkTime = table["_time"][0].to_pydatetime()
  for key, tags in deviation_checks.items():
    # CHECK IF DEVIATION CHECK AVAILABLE
    if len(tags) == AVAILABLE_DEVIATION and pd.Series(tags).isin(table.columns).all():
      #maxVal = max(table[tags[0]].max(), table[tags[1]].max())
      print(tagDict[tags[0]])
      maxVal = tagDict[tags[0]]['max'] - tagDict[tags[0]]['min']
      percentDeviation = abs(table[tags[0]] - table[tags[1]]).max() / maxVal 
      print(maxVal, percentDeviation, tags, DEVIATION_CHECK_VALUE)
      if percentDeviation > DEVIATION_CHECK_VALUE:
        _tags = {"": max, "min": min}
        for idx, tag in enumerate(tags):
          _tags[f"tag_{idx}"] = tag
        points.append({"measurement": "deviation_check", "time": checkTime.isoformat(), "fields": {
          tags[0]: percentDeviation,
          tags[1]: percentDeviation
        }})
  return points
'''
def roc_check(table: pd.DataFrame, devices: List[dict]):
  res = copy.deepcopy(table)
  roc_checks_with_data = pd.DataFrame()
  for col in table.columns:
    max, min = find_low_high_oc_by_devices(devices, col)
    if max is not None and min is not None:
      numerator = 2 * (max - min)
      denominator = (max + min) * (SECOND * CHECK_PERIOD * 2)
      if denominator == 0:
        res[col] = 0
      else:
        rroc = abs(numerator / denominator)
      if rroc > ROC_CHECK_VALUE:
        roc_checks_with_data = pd.concat([pd.DataFrame({"_measurement": "roc_check", col: 1, "_time": DATE_NOW()}, index=[table.index[-1]]), roc_checks_with_data], join="outer")
  return roc_checks_with_data
'''

def frozen_check(table: pd.DataFrame, devices: List[dict]):
  res = copy.deepcopy(table)
  frozen_checks_with_data = pd.DataFrame()
  for col in table.columns:
    max, min = find_low_high_oc_by_devices(devices, col)
    if max is not None and min is not None:
      numerator = 2 * (max - min)
      denominator = (max + min) * (SECOND * CHECK_PERIOD * 2)
      if denominator == 0:
        res[col] = 0
      else:
        rroc = abs(numerator / denominator)
      _, is_frozen_check = get_frozen_check_roc_check_by_tag(col, devices)
      if is_frozen_check:
        if rroc < FROZEN_CHECK_VALUE:
          frozen_checks_with_data = pd.concat([pd.DataFrame({"_measurement": "frozen_check", col: 1, "_time": DATE_NOW()}, index=[table.index[-1]]), frozen_checks_with_data], join="outer")
  return frozen_checks_with_data
