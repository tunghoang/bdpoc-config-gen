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

from influx import Influx, InfluxWriter
from visualize.configs.logger import check_logger
from visualize.utils.common import isNumber

from sendmail import urgentMail, criticalMail, dailyMail
from visualize.utils.tag_utils import load_tag_specs

from check_commons import is_running

end = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
start = end - timedelta(hours=24)
df = Influx().setDebug(True).setBucket(CHECK_BUCKET).from_now(24 * 60).setRate(None).asDataFrame()

mpTagDict = load_tag_specs('assets/files/tag-specs.yaml')
lipTagDict = load_tag_specs('assets/files/lip-tag-specs.yaml')
mr4100TagDict = load_tag_specs('assets/files/mr4100-tag-specs.yaml')
mr4110TagDict = load_tag_specs('assets/files/mr4110-tag-specs.yaml')
glycolTagDict = load_tag_specs('assets/files/glycol-tag-specs.yaml')

df.drop(columns=["result", "_start", "_stop", "table"], inplace=True)

all_nan = {}
all_overange = {}
all_roc = {}
all_irv = {}

def job(df, tagDict, device, start, end):
  #global all_nan, all_overange, all_roc, all_irv
  print(device, is_running(device))

job(df, mpTagDict, 'mp', start, end)  
job(df, lipTagDict, 'lip', start, end)  
job(df, mr4100TagDict, 'mr4100', start, end)  
job(df, mr4110TagDict, 'mr4110', start, end)  
job(df, glycolTagDict, 'glycol', start, end)  
