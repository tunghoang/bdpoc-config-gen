import sys
import time
import warnings
import traceback
from os import path
from threading import Thread
from visualize.configs.logger import check_logger
from dateutil import parser as dparser
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import schedule
from influxdb_client.client.warnings import MissingPivotFunction

sys.path.append(path.join(path.dirname(__file__), "visualize"))
#from configs.query import Query

from visualize.configs.constants import (BUCKET, CHECK_PERIOD, MONITORING_BUCKET, ORG, MINIMUM_RATIO_NAN_ALLOW)
from visualize.configs.influx_client import query_api, write_api
from visualize.configs.logger import check_logger

from visualize.checks.overange_check import do_overange_check
from visualize.checks.roc_check import do_roc_check

from visualize.services.check_services import (do_deviation_check, do_irv_check)
from visualize.utils.tag_utils import load_tag_config
from utils.check_utils import check_gen
from influx import Influx

start = dparser.isoparse("2023-04-10T21:34:00+07:00")
end = dparser.isoparse("2023-04-10T21:44:00+07:00")
instance = Influx().setStart(start).setStop(end).setRate('1s').addFields(["HT_PDI_2183.PV"])
table = instance.setDebug(True).setInterpolation(False).asPivotDataFrame()
table["HT_PDI_2183.PV"] = None
print(table)


def __find_nan(df, tag):
  warnings.filterwarnings("ignore")
  df['idx'] = df.index
  last = df.index[-1]
  print(df.index[-1])
  input("kk")
  
  df['mark'] = df[tag].isnull().astype(int).groupby(df[tag].notnull().astype(int).cumsum()).cumsum()
  df1 = df[df['mark'] <= 1]
  df1['width'] = df1['idx'].shift(-1) - df1['idx']
  lastRow = df1.tail(1).idx.values[0]
  print(lastRow)
  input("pause")
  df1.at[lastRow, 'width'] = last - df1.loc[lastRow, 'idx'] 
  print(df1)

  threshold = (2 * CHECK_PERIOD * 60 * MINIMUM_RATIO_NAN_ALLOW)
  print(threshold)
  results = df1[ ( df1['mark'] == 1 ) & ( df1['width'] >= threshold )]
  if not results.empty:
    results.drop(labels=['idx', 'mark', 'width'], axis=1, inplace=True)
    results.fillna(1, inplace=True)
    results.set_index("_time", inplace=True)
    return results
  return None
  
def __check_nan(table):
  nan_check_results = []

  tag_results = __find_nan(table[["HT_PDI_2183.PV", "_time"]], "HT_PDI_2183.PV")
  if tag_results is not None:
    nan_check_results.append(tag_results)
  if len(nan_check_results) > 0:
    return pd.concat(nan_check_results, axis=1, join="outer")
  return pd.DataFrame()

def do_nan_check(table):
  nan_checks = __check_nan(table)
  print(nan_checks)
  count = len(nan_checks.index)
  for point in check_gen(lambda x:"nan_check", nan_checks):
    print(point)

do_nan_check(table)
