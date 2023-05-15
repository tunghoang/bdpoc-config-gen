import sys
import time
from datetime import datetime, timedelta
from dateutil import parser as dparser
import pandas as pd
import warnings
import traceback
import pytz
from os import path

from influxdb_client.client.warnings import MissingPivotFunction
from influx import Influx

sys.path.append(path.join(path.dirname(__file__), "visualize"))

from sendmail import datasourceMail
from visualize.configs.logger import check_logger

end = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))

df = Influx(
  measurement="py_collector_metric", 
  bucket='monitoring'
).setDebug(True).addField("collect_rate").from_now(5).setRate('2m').asDataFrame()

df = df[["_time","_value", "location", "type"]]
df = df.pivot(index="_time", columns=("location", "type"), values="_value").reset_index()
df.columns = df.columns.to_flat_index().str.join("_")
values = df.values[-1][1:]
failed_sources = []
print(values)
for idx, v in enumerate(values):
  if pd.isnull(v):
    failed_sources.append(df.columns[idx + 1])

if len(failed_sources) > 0:
  check_logger.info(f"Failed sources: {failed_sources}")
  datasourceMail(failed_sources, end)
else:
  check_logger.info("No source failed")
