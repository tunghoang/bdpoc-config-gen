import datetime as dt

import pytz
from utils.env_utils import get_env

# ENVIRONMENT VARIABLES
CUSTOM_DATAFRAME_PREVIEW = get_env("CUSTOM_DATAFRAME_PREVIEW")
CUSTOM_DATAFRAME_RELEASE = get_env("CUSTOM_DATAFRAME_RELEASE") == "True"
OUTSTANDING_TAG_RELEASE = get_env("OUTSTANDING_TAG_RELEASE") == "True"

VIEW_MODES = ("Overview", "Raw Data", "MP Routine Report", "MP Startup Report")
SECOND = 60
# DEFAULT CHART STYLE
# LINE_SHAPE = 'hv'
LINE_SHAPE = 'linear'
#TIME_STRINGS = {10: '10s', 30: '30s', 60: '1m', 120: '2m', 300: '5m', 600: '10m', 1800: '30m', 0: 'Custom...'}
TIME_STRINGS = [
  {300: '5m', 600: '10m', 1800: '30m', 0: 'Custom...'},
  {30: '30s', 60: '1m', 120: '2m', 300: '5m', 600: '10m', 1800: '30m', 0: 'Custom...'},
  {600: '10m', 1800: '30m', 3600: '60m', 7200: '2h', 14400: '4h', 86400: '1d', 172800: '2d', 0: 'Custom...'},
  {86400: '1d', 604800: '1w', 1209600: '2w', 2419200: '4w', 0: 'Custom...'}
]
# DATE TIME NOW
DATE_NOW = lambda: dt.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
DATE_NOW_IN_NS = lambda: int(DATE_NOW().strftime('%s')) * 10**9
# PIVOT OR NOT
PIVOT = True
# CHECKS LIST
CHECKS_LIST = {'none': 'None', 'nan_check': 'NaN-Check', 'overange_check': 'Overange-Check', 'irv_check': 'Instrument-Range-Validation-Check', 'deviation_check': 'Deviation-Check', 'frozen_check': 'Frozen-Check', 'roc_check': 'Rate-Of-Change-Check'}
CHECK_PERIOD = 1 # in minutes
MP_SPEED_CHECK_PERIOD = 10 # in minutes
SPEED_TAG = "HT_XE_2180A.PV"

# INFLUX
BUCKET = "datahub"
CHECK_BUCKET = "check-datahub"
ORG = "BDPOC"
# MIN NUMBER OF NAN VALUE ALLOWED: more than 118 nan samples per 2*CHECK_PERIOD minutes
MINIMUM_RATIO_NAN_ALLOW = 118 / (CHECK_PERIOD * 2 * SECOND)
# AVAILABLE DEVIATION CHECK
AVAILABLE_DEVIATION = 2
# ROC CHECK VALUE
ROC_CHECK_VALUE = 0.05
# DEVIATION CHECK VALUE
DEVIATION_CHECK_VALUE = 0.05
# FROZEN CHECK VALUE
FROZEN_CHECK_VALUE = 0.05/100

# START STOP ROC ROUTINE
START_DERIVATIVE_VALUE = 0.1
STOP_DERIVATIVE_VALUE = -0.1

MONITORING_BUCKET = "monitoring"
MP_EVENTS_BUCKET = 'mp-events'
CHECK_MONITORING_PERIOD = "30m"
MONITORING_PERIOD = "5m"
MONITORING_MEASUREMENT = "collector_metric"
MONITORING_FIELD = "collect_rate"
MONITORING_AGG_WINDOW = '1m'

INFINITIES = (-999999.0, 999999.0)
LABELS = ("LOW", "HIGH")
