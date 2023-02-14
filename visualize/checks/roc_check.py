from configs.constants import CHECK_BUCKET, CHECK_PERIOD, ROC_CHECK_VALUE, FROZEN_CHECK_VALUE
from configs.logger import check_logger
from utils.check_utils import check_gen
from influx import InfluxWriter
import json, math, copy
import pandas as pd
import re
import warnings

def __tagType(tag):
  if tag.startswith('HT_T'):
    return "T"
  if re.search("^HT_[LPF]", tag) is not None:
    return "P"
  if re.search("^HT_[VZX]", tag) is not None:
    return "V"
  return None

def __check_roc(table):
  l = len(table)
  lseg = CHECK_PERIOD * 60
  n = math.ceil(l / lseg)
  print(n)
  indexSeries = pd.Series([i // lseg for i in range(0, l)])
  table['segment'] = indexSeries
  table['mark'] = (indexSeries - indexSeries.shift()).fillna(1.0)
  
  timeSeries = table[table['mark'] == 1]['_time']
  roc_check_result = pd.DataFrame({"_time": timeSeries})
  segs = [ table[table.segment == sIdx] for sIdx in range(0, n) ]
  for col in table.columns:
    tagType = __tagType(col)
    if tagType is None:
      continue
    roc_check_result[col] = [(2*abs(abs(s[col].max()) - abs(s[col].min()))/( ( abs(s[col].max()) + abs(s[col].min()) ) * len(s) ) ) for s in segs]
    #roc_check_result[col] = (roc_check_result[col] > ROC_CHECK_VALUE).astype(float)
  
  if len(roc_check_result.columns) <= 1:
    return pd.DataFrame()
  roc_check_result.set_index('_time', inplace=True)
  return roc_check_result
          

def do_roc_check(table):
  dfcopy = copy.deepcopy(table)
  roc_checks = __check_roc(dfcopy)
  for point in check_gen(
    lambda x: "roc_check" if x > ROC_CHECK_VALUE else "frozen_check",
    roc_checks, 
    lambda x: x > ROC_CHECK_VALUE or x < FROZEN_CHECK_VALUE
  ):
    InfluxWriter().setBucket(CHECK_BUCKET).write(point)
    #write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)
    check_logger.info("roc_frozen_checking 1 point")
  check_logger.info("roc_frozen checking done")
