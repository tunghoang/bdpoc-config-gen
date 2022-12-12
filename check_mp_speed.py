import sys
import time
import warnings
from os import path
from threading import Thread

import numpy as np
import pandas as pd
import schedule
from influxdb_client.client.warnings import MissingPivotFunction
from influxdb_client import Point

sys.path.append(path.join(path.dirname(__file__), "visualize"))
from visualize.configs.constants import (BUCKET, MP_SPEED_CHECK_PERIOD, MP_EVENTS_BUCKET, ORG)
from visualize.configs.influx_client import query_api, write_api
from visualize.configs.logger import check_logger
from visualize.configs.Query import Query
from visualize.utils.fake_data import fake_mp_startup

warnings.simplefilter("ignore", MissingPivotFunction)

SPEED_TAG = "HT_XE_2180A.PV"

def job():
  print("Querying ...")
  query = Query().from_bucket(BUCKET).range(f"{2 * MP_SPEED_CHECK_PERIOD}m").filter_fields(
    [SPEED_TAG]
  ).keep_columns(
    "_time", "_value", "_field"
  ).aggregate_window(False, "10s").pivot(
    "_time", "_field", "_value"
  ).duplicate(
    SPEED_TAG, 'derivative'
  ).derivative(
    non_negative=False, unit="1s", columns=["derivative"]
  ).to_str()
  print(query)
  table = query_api.query_data_frame(query, org=ORG)
  table1 = table[[SPEED_TAG, 'derivative']]
  table1 = table1.interpolate(method='linear', limit_direction='both')
  table[SPEED_TAG] = table1[SPEED_TAG]
  table['derivative'] = table1['derivative']

  def normalizeDerivative(i_v):
    i, v = i_v
    speed = table.at[i, SPEED_TAG]
    return v / speed if speed != 0 else v

  table['derivative'] = pd.Series(map(normalizeDerivative, enumerate(table['derivative'].tolist())))

  #table = fake_mp_startup(table)

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

  firstLineEvent = table.iloc[0].to_dict()
  print(firstLineEvent)
  lastLineEvent = table.iloc[-1].to_dict()
  print(lastLineEvent)

  table = table[table.group > 0]
  table = pd.melt(table, id_vars=["_time", "_start", "_stop", "group", "sign"], value_vars=[SPEED_TAG], var_name="_field", value_name="_value")
  groups = table.groupby('group')
  for name, group in groups:
    signList = group['sign'].tolist()
    timeList = group['_time'].tolist()
    print(timeList[0], timeList[-1], signList[0])
    print(name, "............" )
    if name != firstLineEvent['group'] and name != lastLineEvent['group']:
      p = Point(MP_EVENTS_BUCKET).tag(
        "start", timeList[0]
      ).tag(
        "stop", timeList[-1]
      ).field("type", signList[0]).time(str(timeList[0]))
      write_api.write(MP_EVENTS_BUCKET, ORG, p, 's')

schedule.every(MP_SPEED_CHECK_PERIOD).minutes.do(job)
while True:
  schedule.run_pending()
  time.sleep(1)
#job()
