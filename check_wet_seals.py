import sys
import time
import warnings
import traceback
import pytz
from os import path

from dateutil import parser as dparser
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import schedule
from influxdb_client.client.warnings import MissingPivotFunction

sys.path.append(path.join(path.dirname(__file__), "visualize"))

from visualize.configs.constants import (BUCKET, CHECK_BUCKET, CHECK_PERIOD, MONITORING_BUCKET, ORG)
from visualize.configs.logger import check_logger

from influx import Influx, InfluxWriter
from sendmail import wetGasSealMail
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--start", required=False)
parser.add_argument("-e", "--end", required=False)
args = parser.parse_args()

end = dparser.isoparse(args.end) if args.end else datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))

def findFlushCount(end, sealLevelTag="HT_LI_2122.PV",ndays=3):
  start = dparser.isoparse(args.start) if args.start else (end - timedelta(days=ndays))
  check_logger.info(f"Find FlushCount(ndays={ndays}) {start} --> {end}")
  df = Influx().setRawQuery(f"""
  from(bucket: "{BUCKET}")
    |> range(start: {int(start.timestamp())}, stop: {int(end.timestamp())})
    |> filter(fn: (r) => r["_measurement"] == "phdpeer")
    |> filter(fn: (r) => r["_field"] == "{sealLevelTag}")
    |> filter(fn: (r) => r["_value"] > 0)
    |> aggregateWindow(every: 1m, fn: mean)  
    |> derivative(unit: 10m, nonNegative: false, columns: ["_value"], timeColumn: "_time")
    |> filter(fn: (r) => r["_value"] < -50)
    |> aggregateWindow(every: 20m, fn: max, createEmpty: false)
  """).asDataFrame()
  flush_count = len(df.index) / ndays
  return flush_count  

def findDropLevel(end, ndays=1):
  tank_df = Influx().setStop(end).setStart(end - timedelta(days=ndays)).addField('HT_LI_2110.PV').setRate(None).asDataFrame()
  yesterday_level = tank_df["_value"]._values[0]
  today_level = tank_df["_value"]._values[-1]
  dropLevel = yesterday_level - today_level
  check_logger.info(f"{yesterday_level} {today_level} {dropLevel}")
  return dropLevel

def intepret(flush_count, dropLevel, seal="LP"):
  check_logger.info("-----------")
  check_logger.info(f"{dropLevel}, {flush_count}")

  flush_count_threshold_alarm = 5
  flush_count_threshold_prealarm = 2
  dropLevel_threshold_alarm = 0.5
  dropLevel_threshold_prealarm = 0.4

  if seal == "IP":
    flush_count_threshold_alarm = 4
    flush_count_threshold_prealarm = 2
    dropLevel_threshold_alarm = 0.3
    dropLevel_threshold_prealarm = 0.15

  if flush_count >= flush_count_threshold_alarm:
    if dropLevel > dropLevel_threshold_alarm :
      # Alarm
      check_logger.info("Alarm");
      InfluxWriter().setBucket(CHECK_BUCKET).write({
        "measurement": "Alarm", 
        "time": end.isoformat(), 
        "fields": {f"{seal}_Seal": 1},
        "tags": {"dropLevel": dropLevel, "dischargeCount": flush_count}
      })
      wetGasSealMail([{
        "Field": f"{seal}_Seal", 
        "Description": "Lube Oil seal leak", 
        "dropLevel": dropLevel,
        "flush_count": flush_count
      }], start, end, testing=True)
    else:
      # PreAlarm
      check_logger.info("Prealarm");
      InfluxWriter().setBucket(CHECK_BUCKET).write({
        "measurement": "PreAlarm", 
        "time": end.isoformat(), 
        "fields": {f"{seal}_Seal": 1},
        "tags": {"dropLevel": dropLevel, "dischargeCount": flush_count}
      })
  elif flush_count > flush_count_threshold_prealarm:
    if dropLevel > dropLevel_threshold_prealarm :
      # PreAlarm
      check_logger.info("Prealarm");
      InfluxWriter().setBucket(CHECK_BUCKET).write({
        "measurement": "PreAlarm", 
        "time": end.isoformat(), 
        "fields": {f"{seal}_Seal": 1},
        "tags": {"dropLevel": dropLevel, "dischargeCount": flush_count}
      })
      pass
    else:
      # Normal
      pass
  else:
    # Normal
    pass
  
'''
N_DAYS = 3
df = Influx().setRawQuery(f"""
from(bucket: "{BUCKET}")
  |> range(start: {int(start.timestamp())}, stop: {int(end.timestamp())})
  |> filter(fn: (r) => r["_measurement"] == "phdpeer")
  |> filter(fn: (r) => r["_field"] == "HT_LI_2122.PV")
  |> filter(fn: (r) => r["_value"] > 0)
  |> aggregateWindow(every: 1m, fn: mean)  
  |> derivative(unit: 10m, nonNegative: false, columns: ["_value"], timeColumn: "_time")
  |> filter(fn: (r) => r["_value"] < -50)
  |> aggregateWindow(every: 20m, fn: max, createEmpty: false)
""").asDataFrame()

tank_df = Influx().setStop(end).setStart(end - timedelta(days=1)).addField('HT_LI_2110.PV').setRate(None).asDataFrame()
yesterday_level = tank_df["_value"]._values[0]
today_level = tank_df["_value"]._values[-1]
#dropLevel = (yesterday_level - today_level) * 2 / ( today_level + yesterday_level )
dropLevel = yesterday_level - today_level

check_logger.info(df[["_time", "_field", "_value"]])

flush_count = len(df.index) / N_DAYS
#flush_count = 6
#dropLevel = 0.6
'''
dropLevel = findDropLevel(end)
flush_count = findFlushCount(end)
intepret(flush_count, dropLevel)

flush_count = findFlushCount(end, sealLevelTag="HT_LI_2152.PV", ndays = 13)
intepret(flush_count, dropLevel, seal="IP")

'''
check_logger.info("-----------")
check_logger.info(f"{yesterday_level}, {today_level}, {dropLevel}, {flush_count}")
if flush_count >= 5:
  if dropLevel > 0.5 :
    # Alarm
    check_logger.info("Alarm");
    InfluxWriter().setBucket(CHECK_BUCKET).write({
      "measurement": "Alarm", 
      "time": end.isoformat(), 
      "fields": {"LP_Seal": 1},
      "tags": {"dropLevel": dropLevel, "dischargeCount": flush_count}
    })
    wetGasSealMail([{
      "Field": "HT_LI_2122", 
      "Description": "Lube Oil seal leak", 
      "dropLevel": dropLevel,
      "flush_count": flush_count
    }], start, end, testing=True)
  else:
    # PreAlarm
    check_logger.info("Prealarm");
    InfluxWriter().setBucket(CHECK_BUCKET).write({
      "measurement": "PreAlarm", 
      "time": end.isoformat(), 
      "fields": {"LP_Seal": 1},
      "tags": {"dropLevel": dropLevel, "dischargeCount": flush_count}
    })
elif flush_count > 2:
  if dropLevel > 0.4 :
    # PreAlarm
    check_logger.info("Prealarm");
    InfluxWriter().setBucket(CHECK_BUCKET).write({
      "measurement": "PreAlarm", 
      "time": end.isoformat(), 
      "fields": {"LP_Seal": 1},
      "tags": {"dropLevel": dropLevel, "dischargeCount": flush_count}
    })
    pass
  else:
    # Normal
    pass
else:
  # Normal
  pass
'''
