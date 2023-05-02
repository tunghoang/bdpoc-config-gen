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

from visualize.views.container import irvTableData, tagSpecFile
from influx import Influx, InfluxWriter
from configs.logger import check_logger

warnings.simplefilter("ignore", MissingPivotFunction)

device = 'mp'
start = dparser.isoparse('2023-04-09T05:30:00+07:00')
end = dparser.isoparse('2023-04-09T17:30:00+07:00')
check_logger.info(f"{datetime.now()}: IRV Check run for {device}")
#tagDict = load_tag_specs(tagSpecFile(device))
#irv_fields = list(filter(lambda x: isNumber(tagDict[x]["high"]), tagDict.keys()))
irv_fields = ['HT_FI_2191.PV']

df = Influx().setDebug(True).addFields(
  irv_fields
).setStart(
  start
).setStop(end).asMinMaxDataFrame()
print(df)
records = irvTableData(df, device)
print(records)
df1 = Influx().setDebug(True).addFields(irv_fields).setRate(None).setStart(start).setStop(end).asDataFrame()
print(df1[["_time", "_value", "_measurement"]])
print(df1._value.min())
