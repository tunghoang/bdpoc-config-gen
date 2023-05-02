from configs.constants import CHECK_BUCKET, CHECK_PERIOD, MINIMUM_RATIO_NAN_ALLOW
from configs.logger import check_logger
from utils.check_utils import check_gen
from influx import InfluxWriter
import json, copy
import pandas as pd
import warnings

def __find_nan(df, tag):
  warnings.filterwarnings("ignore")
  df['idx'] = df.index
  last = df.index[-1]

  df['mark'] = df[tag].isnull().astype(int).groupby(df[tag].notnull().astype(int).cumsum()).cumsum()

  df1 = df[df['mark'] <= 1]
  df1['width'] = df1['idx'].shift(-1) - df1['idx']

  lastRow = df1.tail(1).idx.values[0]

  df1.at[lastRow, 'width'] = last - df1.loc[lastRow, 'idx'] 

  threshold = (2 * CHECK_PERIOD * 60 * MINIMUM_RATIO_NAN_ALLOW)
  
  results = df1[ ( df1['mark'] == 1 ) & ( df1['width'] >= threshold )]
  if not results.empty:
    results.drop(labels=['idx', 'mark', 'width'], axis=1, inplace=True)
    results.fillna(1., inplace=True)
    results.set_index("_time", inplace=True)
    return results
  return None

def __check_nan(table, tags):
  if table is None or table.empty or len(tags) == 0:
    return
  nan_check_results = []
  for tag in tags:
    if tag not in table.columns:
      table[tag] = None
    tag_results = __find_nan(table[[tag, "_time"]], tag)
    if tag_results is not None:
      nan_check_results.append(tag_results)
  if len(nan_check_results) > 0:
    return pd.concat(nan_check_results, axis=1, join="outer")
  return pd.DataFrame()
  
def __check_nan_old(table, tags):
  if table is None or table.empty or len(tags) == 0:
    return
  nan_check_results = []
  for tag in table.columns:
    if tag not in tags:
      continue
    tag_results = __find_nan(table[[tag, "_time"]], tag)
    if tag_results is not None:
      nan_check_results.append(tag_results)
  if len(nan_check_results) > 0:
    return pd.concat(nan_check_results, axis=1, join="outer")
  return pd.DataFrame()

def do_nan_check(table, tags):
  dfcopy = copy.deepcopy(table)
  nan_checks = __check_nan(dfcopy, tags)
  count = len(nan_checks.index)
  print(nan_checks)
  print("--------------------")
  for point in check_gen(lambda x:"nan_check", nan_checks):
    print(point)
    InfluxWriter().setBucket(CHECK_BUCKET).write(point)
    #check_logger.info("nan_checking 1 point %s", json.dumps(point, default=str))
  check_logger.info(f"nan_checking done: {count} events")
