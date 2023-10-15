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

from visualize.configs.constants import (BUCKET, CHECK_PERIOD, MONITORING_BUCKET, ORG, CHECK_IRV_PERIOD, CHECK_BUCKET)
from visualize.utils.tag_utils import load_tag_config, load_tag_specs
from visualize.views.container import irvTableData, tagSpecFile
from influx import Influx, InfluxWriter
from visualize.configs.logger import check_logger
from visualize.utils.common import isNumber

from sendmail import sms_query, urgentMail, criticalMail, dailyMail

from check_commons import is_running

control_logic_checks, deviation_checks, devices = load_tag_config()
tags = [tag["tag_number"] for d in devices for tag in d["tags"]]
warnings.simplefilter("ignore", MissingPivotFunction)

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--start")
parser.add_argument("-e", "--end")
args = parser.parse_args()

def saveToInflux(alarms, alarmTypeFn):
  points = []
  for r in alarms:
    prealarmType = alarmTypeFn(r)
    points.append ({
      "time": end.isoformat(),
      "measurement": "irv_check",
      "fields": {r['Field']: r['Min'] if prealarmType == "L" else r["Max"]},
      "tags": { "type": prealarmType, "from": start.isoformat(), "to": end.isoformat() }
    })
  InfluxWriter().setBucket(CHECK_BUCKET).write(points)
  
def job(start, end, device='mp'):
  check_logger.info(f"{datetime.now()}: IRV Check run for {device}")
  tagDict = load_tag_specs(tagSpecFile(device))
  irv_fields = list(
    filter(
      lambda x: isNumber(tagDict[x]["high"]) and not tagDict[x].get("disabled", False),
      tagDict.keys()
    )
  )

#  df = Influx().setDebug(False).addFields(
#    irv_fields
#  ).setStart(
#    start
#  ).setStop(end).asMinMaxDataFrame()

  filter_str = " ".join([('or r._field == "' + f + '"') for f in irv_fields])
  df = Influx().setDebug(True).setRawQuery(f'''data = from(bucket: "datahub-test")
  |> range(start: {int(start.timestamp())}, stop: {int(end.timestamp())})
  |> filter(fn: (r) => r["_field"] == "loremipsum" {filter_str})
  |> stateCount(fn: (r) => r._value == 0 )
  |> filter(fn: (r) => r.stateCount == -1 or r.stateCount > 5)
union(tables: [data |> min() , data |> max() ])
''').asDataFrame()
  records = irvTableData(df, device)

  criticals = list(filter(lambda r: (r['Flag'] > 2 and tagDict[r['Field']]['critical']), records))
  urgents = list(filter(lambda r: (r['Flag'] > 2 and tagDict[r['Field']]['critical'] == False), records))
  prealarms = list(filter(lambda r: (r['Flag'] == 2), records))
  lowprealarms = list(filter(lambda r: (r['Flag'] == 1), records))

  check_logger.info(f"criticalllllllll {criticals}")
  check_logger.info(f"urgenttttttttttt {urgents}" )
  check_logger.info(f"prealarmssssssss {prealarms}")
  check_logger.info(f"lowwwwwwwwwwwwww {lowprealarms}")
  if len(criticals) > 0:
    filtered_criticals = sms_query(criticals, "critical", end)
    criticalMail(filtered_criticals, start, end, device=device, tagDict=tagDict, testing=(device in ('mr4100', 'mr4110', 'glycol')))
    saveToInflux(criticals, lambda r: "LLL" if r["Min"] < r["LLL"] else "HHH")
  if len(urgents) > 0:
    filtered_urgents = sms_query(urgents, "urgent", end)
    urgentMail(filtered_urgents, start, end, device=device, tagDict=tagDict, testing=(device in ('mr4100', 'mr4110', 'glycol')))
    saveToInflux(urgents, lambda r: "LLL" if r["Min"] < r["LLL"] else "HHH")
  if len(prealarms) > 0:
    saveToInflux(prealarms, lambda r: "LL" if r["Min"] < r["LL"] else "HH")
  if len(lowprealarms) > 0:
    saveToInflux(lowprealarms, lambda r: "L" if r["Min"] < r["L"] else "H")

end = dparser.isoparse(args.end) if args.end else datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
start = dparser.isoparse(args.start) if args.start else (end - timedelta(minutes=2*CHECK_IRV_PERIOD))

if is_running('mp'):
  job(start, end, 'mp')
else:
  check_logger.info("check_irv: mp is stop")

if is_running('lip'):
  job(start, end, 'lip')
else:
  check_logger.info("check_irv: lip is stop")

if is_running('mr4100'):
  job(start, end, 'mr4100')
else:
  check_logger.info("check_irv: mr4100 is stop")

if is_running('mr4110'):
  job(start, end, 'mr4110')
else:
  check_logger.info("check_irv: mr4110 is stop")

job(start, end, "glycol")
#job(start, end, 'glycol')
