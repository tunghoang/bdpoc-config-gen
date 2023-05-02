from configs.constants import CHECK_BUCKET, CHECK_PERIOD, FROZEN_CHECK_VALUE, ROC_CHECK_VALUES, TAG_CLASSIFIER
from configs.logger import check_logger
from utils.check_utils import check_gen
from influx import InfluxWriter
import json, math, copy
import pandas as pd
import re
import warnings

def tag_class(tag):
  tokens = tag.split("_")
  if len(tokens) >= 2:
    return TAG_CLASSIFIER.get(f"{tokens[0]}_{tokens[1]}", None)
  return None

def __check_roc(table):
  l = len(table)
  lseg = CHECK_PERIOD * 60
  n = math.ceil(l / lseg)
  indexSeries = pd.Series([i // lseg for i in range(0, l)])
  table['segment'] = indexSeries
  table['mark'] = (indexSeries - indexSeries.shift()).fillna(1.0)
  
  timeSeries = table[table['mark'] == 1]['_time']
  roc_check_result = pd.DataFrame({"_time": timeSeries})
  segs = [ table[table.segment == sIdx] for sIdx in range(0, n) ]
  for col in table.columns:
    tagType = tag_class(col)
    #check_logger.info(tagType)
    if tagType is None:
      continue
    roc_check_result[col] = [(2*abs(abs(s[col].max()) - abs(s[col].min()))/( ( abs(s[col].max()) + abs(s[col].min()) ) * len(s) ) ) for s in segs]
    #roc_check_result[col] = (roc_check_result[col] > ROC_CHECK_VALUE).astype(float)
  
  if len(roc_check_result.columns) <= 1:
    return pd.DataFrame()
  roc_check_result.set_index('_time', inplace=True)
  return roc_check_result
          

def do_roc_check(table):
  # This function performs both roc check and frozen check
  dfcopy = copy.deepcopy(table)
  roc_checks = __check_roc(dfcopy)
  count = 0
  check_logger.info(f"\n{roc_checks}")
  for points in check_gen(
    lambda x: "frozen_check" if x <= FROZEN_CHECK_VALUE else "roc_check",
    roc_checks, 
    lambda col, x: x > ROC_CHECK_VALUES[tag_class(col)] or x <= FROZEN_CHECK_VALUE
  ):
    InfluxWriter().setBucket(CHECK_BUCKET).write(points)
    count = count + len(points)
    check_logger.info(points)
    
  check_logger.info(f"roc_frozen checking done: {count} events")
