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

print(df)

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
  if not is_running(device):
    check_logger.info(f"{device} is not running!!!")
    return;
  mpdf = df[df._field.isin(tagDict.keys())]

  nan = mpdf[mpdf._measurement == "nan_check"]._field.unique()
  overange = mpdf[mpdf._measurement == "overange_check"]._field.unique()
  roc = mpdf[mpdf._measurement == "roc_check"]._field.unique()
  irv = mpdf[mpdf._measurement == "irv_check"]._field.unique()

  #device = "mp"
  #all_nan[device] = nan
  #all_overange[device] = overange
  #all_roc[device] = roc
  #all_irv[device] = irv
  testing = device in ('glycol',)
  check_logger.info(f"Send daily mail for {device} !!!")
  dailyMail(nan=nan, overange=overange, roc=roc, irv=irv, tagDict=tagDict, device=device, start=start, end=end, testing=testing)

job(df, mpTagDict, 'mp', start, end)  
job(df, lipTagDict, 'lip', start, end)  
job(df, mr4100TagDict, 'mr4100', start, end)  
job(df, mr4110TagDict, 'mr4110', start, end)  
job(df, glycolTagDict, 'glycol', start, end)  
'''
# MP -----------
mpdf = df[df._field.isin(mpTagDict.keys())]

nan = mpdf[mpdf._measurement == "nan_check"]._field.unique()
overange = mpdf[mpdf._measurement == "overange_check"]._field.unique()
roc = mpdf[mpdf._measurement == "roc_check"]._field.unique()
irv = mpdf[mpdf._measurement == "irv_check"]._field.unique()

device = "mp"
all_nan[device] = nan
all_overange[device] = overange
all_roc[device] = roc
all_irv[device] = irv
dailyMail(nan=nan, overange=overange, roc=roc, irv=irv, tagDict=mpTagDict, device=device, start=start, end=end)

# LIP ------------
lipdf = df[df._field.isin(lipTagDict.keys())]

nan = lipdf[lipdf._measurement == "nan_check"]._field.unique()
overange = lipdf[lipdf._measurement == "overange_check"]._field.unique()
roc = lipdf[lipdf._measurement == "roc_check"]._field.unique()
irv = lipdf[lipdf._measurement == "irv_check"]._field.unique()

device = "lip"
all_nan[device] = nan
all_overange[device] = overange
all_roc[device] = roc
all_irv[device] = irv
dailyMail(nan=nan, overange=overange, roc=roc, irv=irv, tagDict=lipTagDict, device=device, start=start, end=end)

# MR4100 ------------
mr4100df = df[df._field.isin(mr4100TagDict.keys())]

nan = mr4100df[mr4100df._measurement == "nan_check"]._field.unique()
overange = mr4100df[mr4100df._measurement == "overange_check"]._field.unique()
roc = mr4100df[mr4100df._measurement == "roc_check"]._field.unique()
irv = mr4100df[mr4100df._measurement == "irv_check"]._field.unique()

device = "mr4100"
all_nan[device] = nan
all_overange[device] = overange
all_roc[device] = roc
all_irv[device] = irv
dailyMail(nan=nan, overange=overange, roc=roc, irv=irv, tagDict=mr4100TagDict, device=device, start=start, end=end)

# MR4110 ------------
mr4110df = df[df._field.isin(mr4110TagDict.keys())]

nan = mr4110df[mr4110df._measurement == "nan_check"]._field.unique()
overange = mr4110df[mr4110df._measurement == "overange_check"]._field.unique()
roc = mr4110df[mr4110df._measurement == "roc_check"]._field.unique()
irv = mr4110df[mr4110df._measurement == "irv_check"]._field.unique()

device = "mr4110"
all_nan[device] = nan
all_overange[device] = overange
all_roc[device] = roc
all_irv[device] = irv
dailyMail(nan=nan, overange=overange, roc=roc, irv=irv, tagDict=mr4110TagDict, device=device, start=start, end=end)

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
dailyMail(nan=nan, overange=overange, roc=roc, irv=irv, tagDict=glycolTagDict, device=device, start=start, end=end, testing=True)
'''
