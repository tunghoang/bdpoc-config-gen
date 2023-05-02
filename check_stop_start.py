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
start = dparser.isoparse(args.start) if args.start else (end - timedelta(minutes=2*CHECK_IRV_PERIOD))

def job(start, end, device='mp'):
  check_logger.info(f"{datetime.now()}: {device.upper()} Check transient condition runs")
  df = Influx().setDebug(True).from_now(60*24*90).addField(runningIndicator(device)).setRate(None).setTail(2).asDataFrame()

  check_logger.info(f"""-------------
  {df}
  """)

  if len(df.index) < 2:
    return

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

job(start, end, 'mp')
job(start, end, 'lip')
