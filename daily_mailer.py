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

from sendmail import urgentMail, criticalMail, dailyMail, testDailyMail
from visualize.utils.tag_utils import load_tag_specs

end = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
start = end - timedelta(hours=24)
df = Influx().setDebug(True).setBucket(CHECK_BUCKET).from_now(24 * 60).setRate(None).asDataFrame()

mpTagDict = load_tag_specs('assets/files/tag-specs.yaml')
lipTagDict = load_tag_specs('assets/files/lip-tag-specs.yaml')

df.drop(columns=["result", "_start", "_stop", "table"], inplace=True)
mpdf = df[df._field.isin(mpTagDict.keys())]

nan = mpdf[mpdf._measurement == "nan_check"]._field.unique()
overange = mpdf[mpdf._measurement == "overange_check"]._field.unique()
roc = mpdf[mpdf._measurement == "roc_check"]._field.unique()
irv = mpdf[mpdf._measurement == "irv_check"]._field.unique()

dailyMail(nan=nan, overange=overange, roc=roc, irv=irv, start=start, end=end)

lipdf = df[df._field.isin(lipTagDict.keys())]

nan = lipdf[lipdf._measurement == "nan_check"]._field.unique()
overange = lipdf[lipdf._measurement == "overange_check"]._field.unique()
roc = lipdf[lipdf._measurement == "roc_check"]._field.unique()
irv = lipdf[lipdf._measurement == "irv_check"]._field.unique()

testDailyMail(nan=nan, overange=overange, roc=roc, irv=irv, start=start, end=end)
