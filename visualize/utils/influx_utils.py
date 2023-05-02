import numpy as np
import pandas as pd
from configs.constants import (BUCKET, CHECK_BUCKET, CHECK_MONITORING_PERIOD, CHECK_PERIOD, CHECKS_LIST, MONITORING_AGG_WINDOW, MONITORING_BUCKET, MONITORING_FIELD, MONITORING_MEASUREMENT, MONITORING_PERIOD, MP_EVENTS_BUCKET, ORG, PIVOT, SECOND, RUNNING_INDICATORS)
from configs.influx_client import query_api
from configs.module_loader import *
from configs.query import Query
from services.influx_services import (get_check, get_check_harvest_rate, get_database, get_tag_harvest_rate)
from utils.fake_data import fake_mp_startup
from utils.tag_utils import load_tag_specs
from dateutil import parser as dparser

from utils.session import sess
from utils.common import isNumber
from configs.logger import check_logger

from influx import Influx

warnings.simplefilter("ignore", MissingPivotFunction)

def get_raw_data(start_date, start_time, end_date, end_time, tags, rate = '30s'):
  __start = dparser.isoparse(f"{start_date}T{start_time}+07:00")
  __end = dparser.isoparse(f"{end_date}T{end_time}+07:00")

  if len(tags) == 0:
    return
  df = Influx().addFields(tags).setDebug(True).setStart(__start).setStop(__end).setRate(rate).asDataFrame()
  return df
  
def query_raw_data(time: int, device: str, tags: list = [], interpolated: bool = False, missing_data: str = "NaN") -> DataFrame:
  if len(tags) == 0:
    return DataFrame()
  query = Query().from_bucket(BUCKET).range(time)
  # if device:
  #   query = query.filter_measurement(device)
  query = query.filter_fields(tags).keep_columns("_time", "_value", "_field").aggregate_window(True if missing_data == "NaN" else False).to_str()
  table = get_database(query)
  if interpolated:
    test = table["_time"]
    table = table.drop(columns=["_time", "_start", "_stop"]).interpolate(method='linear', limit_direction='both', axis=0).assign(_time=test)
  return table

def query_irv_tags(start, end):
  fileName = 'assets/files/tag-specs.yaml' if sess("current_machine") == "mp" else 'assets/files/lip-tag-specs.yaml'
  tagDict = load_tag_specs(fileName)

  irv_fields = list(filter(lambda x: isNumber(tagDict[x]["high"]), tagDict.keys()))
  table = Influx().setDebug(True).addFields(irv_fields).setStart(start).setStop(end).asMinMaxDataFrame()
  return table

def query_irv_tags_old(time: int) -> DataFrame:
  tagDict = load_tag_specs()

  irv_fields = list(filter(lambda x: tagDict[x]["high"] is not None, tagDict.keys()))
  #query = Query().from_bucket(BUCKET).range(time).filter_fields(irv_fields).keep_columns("_time", "_measurement", "_value", "_field").aggregate_window(False).to_str()
  query = Query().from_bucket(BUCKET).range(time).filter_fields(irv_fields).keep_columns("_time", "_measurement", "_value", "_field").to_str()

  query = f"""
    data = {query}

    maxTable = data
      |> max()
    minTable = data
      |> min()
    union(tables: [maxTable, minTable])
  """
  results = query_api.query_data_frame(query, org=ORG)
  if type(results) == list:
    return pd.concat(results)
  return results


SPEED_TAG = "HT_XE_2180A.PV"

def query_transient_periods(start,end, device="mp"):
  inst = Influx().setStart(start).setStop(end).setRate(None).addField(RUNNING_INDICATORS.get(device))
  queryStr = inst.getQuery()
  check_logger.info(f'''---- query ---
{queryStr}
----
  ''')
  df = inst.asDataFrame()
  if (df.empty):
    return df
  df._value = df._value.apply(lambda x: 1 if x == "ON" else 0)
  shift1 = df._value.shift()
  df._value = df._value - shift1
  df1 = df[df._value.notnull() & df._value != 0]
  return df1
def query_mp_transient_periods(start, end):
  inst = Influx().setStart(start).setStop(end).setRate(None).addField('HT_KM_2180.AND_RUNNING.OUT')
  queryStr = inst.getQuery()
  check_logger.info(f'''---- query ---
{queryStr}
----
  ''')
  df = inst.asDataFrame()
  df._value = df._value.apply(lambda x: 1 if x == "ON" else 0)
  shift1 = df._value.shift()
  df._value = df._value - shift1
  df1 = df[df._value.notnull() & df._value != 0]
  return df1

'''
def query_mp_transient_periods_old1(start, end):
  return Influx(measurement="mp-events").setStart(start).setStop(end).setBucket(MP_EVENTS_BUCKET).addFields(['startup', 'shutdown']).asDataFrame()

def query_mp_transient_periods_old(time):
  query = Query().from_bucket(MP_EVENTS_BUCKET).range(time).filter_measurement("mp-events").to_str()
  table = query_api.query_data_frame(query, org=ORG)
  if type(table) == list:
    results = pd.concat(table)
    return results
  return table
'''

def validFn(tagDict, x):
  to = tagDict[x]
  if not to['mp_startup'] : 
    return False
  elif type(to['low']) == str:
    return False
  elif type(to['low2']) == str:
    return False
  elif type(to['low3']) == str:
    return False
  elif type(to['high']) == str:
    return False
  elif type(to['high2']) == str:
    return False
  elif type(to['high3']) == str:
    return False
  return True

def query_irv_transient_tags(start, end, alert_type="STOP"):
  fileName = 'assets/files/tag-specs.yaml' if sess("current_machine") == "mp" else 'assets/files/lip-tag-specs.yaml'
  tagDict = load_tag_specs(fileName)

  irv_fields = list(filter(lambda x: validFn(tagDict, x), tagDict.keys()))
  check_logger.info(f"""
------------- irv_fields startup {len(irv_fields)} ---------
{irv_fields}
-------------------------------------
  """)
  table = Influx().setDebug(True).addFields(irv_fields).setStart(start).setStop(end).asMinMaxDataFrame()
  table['alert_type'] = alert_type
  table["startTime"] = start
  return table

def query_roc_tags(time: int) -> DataFrame:
  tagDict = load_tag_specs()
  tagDict = {k: v for k, v in tagDict.items() if v["mp_startup"]}

  fields = list(tagDict.keys())
  fields.append(SPEED_TAG)

  #query = Query().from_bucket(BUCKET).range(time).filter_fields(list(tagDict.keys())).aggregate_window(True, "1m").keep_columns("_time", "_value", "_field").duplicate("_value", "derivative").derivative(columns=["derivative"]).to_str()

  query = Query().from_bucket(BUCKET).range(time).filter_fields(fields).keep_columns("_time", "_value", "_field").aggregate_window(False, "10s").pivot("_time", "_field", "_value").duplicate(SPEED_TAG, 'derivative').derivative(non_negative=False, unit="1s", columns=["derivative"]).to_str()
  table = query_api.query_data_frame(query, org=ORG)
  fields.append('derivative')
  fields = [f for f in fields if f in table.columns]
  table1 = table[fields]
  table1 = table1.interpolate(method='linear', limit_direction='both')
  for f in fields:
    table[f] = table1[f]

  def transformDerivative(i_v):
    i, v = i_v
    speed = table.at[i, SPEED_TAG]
    return v / speed if speed != 0 else v

  table['derivative'] = pd.Series(map(transformDerivative, enumerate(table['derivative'].tolist())))

  # table = table[table["_value"].notna()]

  """
  Fake data for testing
  """
  # table = fake_mp_startup(table)
  cols = table.columns.tolist()
  # Detecting start/stop periods
  table["sign"] = np.sign(table["derivative"])
  table["group"] = None

  def transition(info, target):
    if info["state"] == target:
      pass
    else:
      if info["state"] == 'normal':
        info["cnt"] = info["cnt"] + 1
      info["state"] = target

  _info = dict(state="normal", cnt=0)

  for rowIdx, row in table.iterrows():
    if abs(row[cols.index("derivative")]) < 0.1:
      transition(_info, "normal")
    elif row[cols.index("derivative")] > 0:
      transition(_info, 'increasing')
      table.at[rowIdx, 'group'] = _info["cnt"]
    elif row[cols.index("derivative")] < 0:
      transition(_info, 'decreasing')
      table.at[rowIdx, 'group'] = _info["cnt"]
  table = table[table.group > 0]

  #return table
  return pd.melt(table, id_vars=["_time", "_start", "_stop", "group", "sign"], value_vars=[f for f in fields if f != "derivative"], var_name="_field", value_name="_value")


def query_check_data(time: int, device: str, tags: list = [], check_mode='none') -> DataFrame:
  if (not device) or (len(tags) == 0) or check_mode == 'none':
    return DataFrame()
  query = Query().from_bucket(CHECK_BUCKET).range(time)
  if check_mode != 'all':
    query.filter_measurement(check_mode)
  query = query.filter_fields(tags).to_str()
  table = get_check(query)
  if table.empty:
    assert Exception("No data found")
  return table

def query_check_all(start, end):
  table = Influx().setDebug(True).setBucket(CHECK_BUCKET).setStart(start).setStop(end).asDataFrame()
  table.to_csv('/tmp/query.all.csv')
  return table
  
def query_check_all_old(time: int) -> DataFrame:
  query = Query().from_bucket(CHECK_BUCKET).range(time).to_str()
  table = get_check(query)
  return table


def dataframe_to_dictionary(df, measurement):
  df["_time"] = to_datetime(df['_time'], errors='coerce').astype(np.int64)
  lines = [{"measurement": f"{measurement}", "tags": {"device": row["_measurement"]}, "fields": {row["_field"]: float(row["_value"])}, "time": row["_time"]} for _, row in df.iterrows() if row["_value"] != 0 and not math.isnan(row["_value"])]
  return lines


def collector_status() -> float:
  df = Influx(measurement="collector_metric", bucket='monitoring').addField("collect_rate").from_now(5).asDataFrame()
  result = None
  if df is None or df.empty:
    result = 0
  else:
    result = df["_value"].values[-1]
  #query = Query().from_bucket(MONITORING_BUCKET).range(MONITORING_PERIOD).filter_measurement(MONITORING_MEASUREMENT).filter_fields([MONITORING_FIELD]).aggregate_window(False, MONITORING_AGG_WINDOW).to_str()
  #result = get_tag_harvest_rate(query)
  return "{:.2f}".format(result)


def check_status() -> float:
  df = Influx(measurement="check_harvest", bucket='monitoring').from_now(30).setRate('1m').setFillPrevious(True).asDataFrame()

  result = 0
  if df is not None and not df.empty:
    result = df["_value"].mean()
  #query = Query().from_bucket(MONITORING_BUCKET).range(CHECK_MONITORING_PERIOD).filter_measurement("check_harvest").aggregate_window(True, MONITORING_AGG_WINDOW).fill().to_str()
  #result = get_check_harvest_rate(query) * (len(CHECKS_LIST.keys()) - 1) * SECOND * (CHECK_PERIOD * 2)
  return "{:.2f}".format(result)
