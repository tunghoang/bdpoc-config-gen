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
# GLYCOL ------------
glycoldf = df[df._field.isin(glycolTagDict.keys())]

nan = glycoldf[glycoldf._measurement == "nan_check"]._field.unique()
overange = glycoldf[glycoldf._measurement == "overange_check"]._field.unique()
roc = glycoldf[glycoldf._measurement == "roc_check"]._field.unique()
irv = glycoldf[glycoldf._measurement == "irv_check"]._field.unique()

device = "glycol"
all_nan[device] = nan
all_overange[device] = overange
all_roc[device] = roc
all_irv[device] = irv
dailyMail(nan=nan, overange=overange, roc=roc, irv=irv, tagDict=glycolTagDict, device=device, start=start, end=end)
