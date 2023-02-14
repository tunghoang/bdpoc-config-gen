from configs.constants import CHECK_BUCKET
from configs.logger import check_logger
from utils.check_utils import check_gen, find_low_high_oc_by_devices
from influx import InfluxWriter
import json, math, copy
import pandas as pd
import warnings

def __find_overange(table, tag, devices):
  warnings.filterwarnings("ignore")
  max, min = find_low_high_oc_by_devices(devices, tag)
  def f(col):
    if col.name == "_time":
      return col
    
    if min is not None and max is not None:
      return (col > max).astype(int) + ((col < min).astype(int) * (-1))
    elif min is not None:
      return (col < min).astype(int) * (-1)
    elif max is not None:
      return (col > max).astype(int)
    return 0
  
  table = table[table[tag].notnull()]
  table = table.apply(f)
  table['c1'] = (table[tag] != 0).astype(int).groupby((table[tag] == 0).astype(int).cumsum()).cumsum()
  table1 = table[ table['c1'] == 1 ]
  table1.drop(labels=['c1'], axis=1, inplace=True)
  table1.set_index('_time', inplace=True)
  return table1

def __check_overange(df, devices, tags = []):
  if df is None or df.empty or len(tags) == 0:
    return
  
  overange_check_results = []
  for tag in df.columns:
    if tag not in tags:
      df.drop(labels=[tag], axis=1, inplace=True)
      continue
    tag_result = __find_overange(df[["_time", tag]], tag, devices)
    if tag_result is not None:
      overange_check_results.append(tag_result)
  if len(overange_check_results) > 0:
    return pd.concat(overange_check_results, axis=1, join='outer')
  return pd.DataFrame()
  
def do_overange_check(table, tags, devices):
  dfcopy = copy.deepcopy(table)
  overange_checks = __check_overange(dfcopy, devices, tags)
  for row in check_gen(lambda x: "overange_check", overange_checks, lambda x: not math.isnan(x)):
    print(row)
    InfluxWriter().setBucket(CHECK_BUCKET).write(row)
    #write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)
    check_logger.info(f"At {row[0]['time']} overange_checking {len(row)} tags")
  check_logger.info("overange_checking done")