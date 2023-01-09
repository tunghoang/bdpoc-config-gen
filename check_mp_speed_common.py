import sys
import warnings
import numpy as np
import pandas as pd

from os import path

from influxdb_client.client.warnings import MissingPivotFunction
from influxdb_client import Point

sys.path.append(path.join(path.dirname(__file__), "visualize"))
from visualize.configs.constants import (MP_EVENTS_BUCKET, SPEED_TAG, ORG)
from visualize.configs.influx_client import query_api, write_api

warnings.simplefilter("ignore", MissingPivotFunction)
from visualize.utils.fake_data import fake_mp_startup


def process(query):
  table = query_api.query_data_frame(query, org=ORG)
  if table.empty:
      print("Empty")
      return
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
  for _, row in table.iterrows():
    print(row.to_dict())
  print("........")
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
    print(timeList)
    print(signList)
    print(name, "............" )
    print(group)
    print("---")
    if name != firstLineEvent['group'] and name != lastLineEvent['group']:
      p = Point(MP_EVENTS_BUCKET).tag(
        "start", timeList[0]
      ).tag(
        "stop", timeList[-1]
      ).field("type", signList[0]).time(str(timeList[0]))
      write_api.write(MP_EVENTS_BUCKET, ORG, p, 's')

