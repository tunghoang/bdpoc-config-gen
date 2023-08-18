import sys
from os import path
from influx import Influx, InfluxWriter
from datetime import datetime, timedelta
from dateutil import parser as dparser
import pytz
sys.path.append(path.join(path.dirname(__file__), "visualize"))
from configs.constants import CHECK_IRV_PERIOD, BUCKET
from configs.logger import check_logger

from sendmail import transientMail
from check_commons import runningIndicator
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--start")
parser.add_argument("-e", "--end")
args = parser.parse_args()

end = dparser.isoparse(args.end) if args.end else datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
start = dparser.isoparse(args.start) if args.start else (end - timedelta(minutes=3*CHECK_IRV_PERIOD))

def job(start, end, device='mp'):
  check_logger.info(f"Start: {start} - End: {end}: {device.upper()} Check transient condition runs")
  runIndicator = runningIndicator(device)
  df = Influx().setDebug(True).setStart(start).setStop(end).addField(runIndicator).setRate(None).asDataFrame()
  l = len(df.index)
  print(l)
  if l < 2:
    df = Influx().setDebug(True).from_now(60*24*90).addField(runIndicator).setRate(None).setTail(2).asDataFrame()
  if l == 0:
    point = {
      "measurement": "phdpeer", 
      "time": (start - timedelta(seconds=30)).isoformat(), 
      "fields": {
        runningIndicator(device): df._value[1]
      }
    }
    InfluxWriter().setBucket(BUCKET).write(point)

  check_logger.info(f"""-------------
  {df[['_time', '_value', '_field']]}
  """)

  if len(df.index) < 2:
    return

  df['_value1'] = df['_value'].apply(lambda x: 0 if x == 'OFF' else 1)
  df['_value_shifted'] = df['_value1'].shift()
  df['_change'] = df._value1 - df._value_shifted
  df_event = df[df['_value_shifted'].notnull() & df['_change'] != 0]

  if df_event._time.apply(lambda t: t.to_pydatetime() > start).any():
    transientMail(df_event._value.iloc[0], start, end, device=device)
  else:
    check_logger.info("No stop start")
'''
  if df._time[1].to_pydatetime() > start:
    if df._value[0] != df._value[1]:
      transientMail(df._value[1], start, end, device=device)
    else:
      check_logger.info("No stop start")
  else:
    check_logger.info("No new event")
    point = {
      "measurement": "phdpeer", 
      "time": (start - timedelta(seconds=30)).isoformat(), 
      "fields": {
        runningIndicator(device): df._value[1]
      }
    }
    InfluxWriter().setBucket(BUCKET).write(point)
'''
job(start, end, 'mp')
job(start, end, 'lip')
job(start, end, 'mr4100')
job(start, end, 'mr4110')
