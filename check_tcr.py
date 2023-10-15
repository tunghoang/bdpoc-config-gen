import sys
import time
import warnings
import traceback
import pytz
from os import path

from dateutil import parser as dparser
from datetime import datetime, timedelta

from influxdb_client.client.warnings import MissingPivotFunction

sys.path.append(path.join(path.dirname(__file__), "visualize"))

from visualize.configs.constants import (BUCKET, CHECK_PERIOD, MONITORING_BUCKET, ORG, CHECK_IRV_PERIOD, CHECK_BUCKET, VIBRATION_TAGS, VIBRATION_THRESHOLDS, VIBRATION_DURATIONS, VIBRATION_SAMPLE_RATE)
from visualize.utils.tag_utils import load_tag_config, load_tag_specs
from visualize.views.container import irvTableData, tagSpecFile
from influx import Influx, InfluxWriter
from visualize.configs.logger import check_logger
from visualize.utils.common import isNumber

from sendmail import urgentMail, criticalMail, dailyMail, vibrationMail

warnings.simplefilter("ignore", MissingPivotFunction)

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--start")
parser.add_argument("-e", "--end")
args = parser.parse_args()

def saveToInflux(alarms, alarmType, measurement="vibration_check"):
  points = []
  for r in alarms:
    points.append ({
      "time": r["_time"].isoformat(),
      "measurement": measurement,
      "fields": {r['_field']: r['_value']},
      "tags": { "type": alarmType }
    })
  InfluxWriter().setBucket(CHECK_BUCKET).write(points)

def query_vibration_data(tagNames, start, end):
    query = f'''
data = from(bucket: "datahub-test")
    |> range(start: {int(start.timestamp())}, stop: {int(end.timestamp())})
    |> filter(fn: (r) => r._field == "loremipsum" or {" or ".join([('r._field == "' + tag + '"') for tag in tagNames])})
    |> aggregateWindow(every: {VIBRATION_SAMPLE_RATE}s, fn: mean, createEmpty: false)
alarm = data |> stateCount(fn: (r) => r._value > {VIBRATION_THRESHOLDS["ALARM"]} and r._value <= {VIBRATION_THRESHOLDS["SHUTDOWN"]})
    |> filter(fn: (r) => r.stateCount > {VIBRATION_DURATIONS["ALARM"]})
    |> set(key: "alarmType", value: "ALARM")
shutdown = data |> stateCount(fn: (r) => r._value > {VIBRATION_THRESHOLDS["SHUTDOWN"]})
    |> filter(fn: (r) => r.stateCount > {VIBRATION_DURATIONS["SHUTDOWN"]})
    |> set(key: "alarmType", value: "CRITICAL")
union(tables: [alarm, shutdown])
'''

    df = Influx().setDebug(True).setRawQuery(query).asDataFrame()
    if df.empty:
        return [[], []]
    return df[df.alarmType == "ALARM"].drop_duplicates(subset="_field").to_dict("records"), df[df.alarmType == "CRITICAL"].drop_duplicates(subset="_field").to_dict("records")

def job(start, end, device='mr4100'):
  check_logger.info(f"{start} - {end}: VIBRATION Check run for {device}")
  tagDict = load_tag_specs(tagSpecFile(device))
  vibration_fields = VIBRATION_TAGS[device]
  alarm, shutdown = query_vibration_data(vibration_fields, start, end)
  print(len(alarm), len(shutdown))
  if len(alarm) > 0:
    saveToInflux(alarm, "ALARM")
    vibrationMail(alarm, tagDict=tagDict, device=device, testing=True)
    pass
  else:
    check_logger.info("No VIBRATION Alarm")

  if len(shutdown) > 0:
    saveToInflux(shutdown, "CRITICAL")
    vibrationMail(shutdown, tagDict=tagDict, device=device, testing=True)
    pass
  else:
    check_logger.info("No VIBRATION Shutdown (critical)")

end = dparser.isoparse(args.end) if args.end else datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
start = dparser.isoparse(args.start) if args.start else (end - timedelta(minutes=6*CHECK_IRV_PERIOD))

job(start, end, device='mr4100')
job(start, end, device='mr4110')
