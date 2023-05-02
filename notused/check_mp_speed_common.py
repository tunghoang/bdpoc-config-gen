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

def writeEvent(firstEvent):
  print(firstEvent["_time"], firstEvent["_time"].isoformat())
  sTime = firstEvent["_time"].isoformat()
  p = Point(MP_EVENTS_BUCKET).tag(
          "start", sTime
  ).field(
          "startup" if firstEvent['sign'] > 0 else "shutdown", 1
  ).time(sTime)
  write_api.write(MP_EVENTS_BUCKET, ORG, p, 's')

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

  table['sign_shift'] = table['sign'].shift()
  table['cumsum'] = (table['sign'] != table['sign_shift']).cumsum()

  groups = table.groupby('cumsum')
  for g in groups:
    firstEvent = g[1].iloc[0].to_dict()
    lastEvent = g[1].iloc[-1].to_dict()
    sign = firstEvent['sign']
    if sign > 0:
      normIncrease = ( lastEvent[SPEED_TAG] - firstEvent[SPEED_TAG] ) / lastEvent[SPEED_TAG]
      if normIncrease > 0.7:
        writeEvent(firstEvent)
    elif sign < 0:
      if lastEvent[SPEED_TAG] == 0:
        writeEvent(firstEvent)
