import warnings

import numpy as np
import pandas as pd


def check_gen(type: str, checks: pd.DataFrame):
  for time, row in checks.iterrows():
    points = []
    for col in checks.columns:
      if row[col] != 0 and col != "_time" and col != "_measurement":
        points.append({"measurement": f"{type}", "time": time, "fields": {col: row[col]}})
    yield points


def find_low_high_oc_by_series(col: pd.Series) -> tuple:
  if col.size == 0:
    return None, None
  with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=RuntimeWarning)
    max = np.nanmax(col)
    min = np.nanmin(col)
    return max, min


def find_low_high_oc_by_devices(devices: list, tag: str) -> tuple:
  for device in devices:
    for t in device["tags"]:
      if t["tag_number"] == tag and "overange_check" in t["checks"]:
        return t["checks"]["overange_check"]["high"], t["checks"]["overange_check"]["low"]
  return None, None


def find_low_high_irv_by_series(col: pd.Series) -> tuple:
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


def find_low_high_irv_by_devices(devices: list, tag: str) -> tuple:
  for device in devices:
    for t in device["tags"]:
      if t["tag_number"] == tag and "irv_check" in t["checks"]:
        return t["checks"]["irv_check"]["high3"], t["checks"]["irv_check"]["high2"], t["checks"]["irv_check"]["high"], t["checks"]["irv_check"]["low"], t["checks"]["irv_check"]["low2"], t["checks"]["irv_check"]["low3"]
  return None, None, None, None, None, None


def get_roc_check_by_tag(tag_check: str, devices: list):
  for device in devices:
    for tag in device["tags"]:
      if tag["tag_number"] == tag_check:
        if "roc_check" in tag["checks"]:
          return tag["checks"]["roc_check"]
  return None


def get_frozen_check_roc_check_by_tag(tag_check: str, devices: list):
  for device in devices:
    for tag in device["tags"]:
      if tag["tag_number"] == tag_check:
        if "roc_check" in tag["checks"] and "frozen_check" in tag["checks"]:
          return tag["checks"]["roc_check"], tag["checks"]["frozen_check"]
  return None, None
