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

from sendmail import urgentMail, criticalMail, dailyMail

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
  irv_fields = list(filter(lambda x: isNumber(tagDict[x]["high"]), tagDict.keys()))

  df = Influx().setDebug(False).addFields(
    irv_fields
  ).setStart(
    start
  ).setStop(end).asMinMaxDataFrame()

  records = irvTableData(df, device)

  criticals = list(filter(lambda r: (r['Flag'] > 2 and tagDict[r['Field']]['critical']), records))
  urgents = list(filter(lambda r: (r['Flag'] > 2 and tagDict[r['Field']]['critical'] == False), records))
  prealarms = list(filter(lambda r: (r['Flag'] == 2), records))
  lowprealarms = list(filter(lambda r: (r['Flag'] == 1), records))

  if len(criticals) > 0:
    criticalMail(criticals, start, end, device=device, testing=(device == 'lip'))
    #criticalMail(criticals, start, end, device=device, testing=True)
    saveToInflux(criticals, lambda r: "LLL" if r["Min"] < r["LLL"] else "HHH")
  if len(urgents) > 0:
    urgentMail(urgents, start, end, device=device, testing=(device == 'lip'))
    #urgentMail(urgents, start, end, device=device, testing=True)
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
