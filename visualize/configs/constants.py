import datetime as dt

import pytz
from utils.env_utils import get_env

OVERVIEW = 0
RAW_DATA = 1
ROUTINE_REPORT = 2
TRANSIENT_REPORT = 3
WET_SEALS = 4
REMAINING_USEFUL_LIFE = 5
#VIBRATION_MONITORING = 6 # TCR

# ENVIRONMENT VARIABLES
CUSTOM_DATAFRAME_PREVIEW = get_env("CUSTOM_DATAFRAME_PREVIEW")
CUSTOM_DATAFRAME_RELEASE = get_env("CUSTOM_DATAFRAME_RELEASE") == "True"
OUTSTANDING_TAG_RELEASE = get_env("OUTSTANDING_TAG_RELEASE") == "True"


VIEW_MODES = {
  "mp": {
    0: "Overview", 
    1: "Raw Data", 
    2: "MP Routine Report", 
    3: "MP Transient Report", 
    5: "Remaining Useful Life"
  }, 
  "lip": {
    0: "Overview", 
    1: "Raw Data", 
    2: "LIP Routine Report", 
    3: "LIP Transient Report", 
    4: "Wet Seals"
  },
  "mr4100": {
    0: "Overview", 
    1: "Raw Data", 
    2: "MR4100 Routine Report", 
    3: "MR4100 Transient Report",
    #6: "Vibration Monitoring"
  },
  "mr4110": {
    0: "Overview", 
    1: "Raw Data", 
    2: "MR4110 Routine Report", 
    3: "MR4110 Transient Report", 
    #6: "Vibration Monitoring"
  },
  "glycol": {
    0: "Overview",
    1: "Raw Data",
    2: "Glycol Routine Report"
  }
}
#VIEW_MODES = {
#  "mp": ("Overview", "Raw Data", "MP Routine Report", "MP Transient Report", "", "Remaining Useful Life"), 
#  "lip": ("Overview", "Raw Data", "LIP Routine Report", "LIP Transient Report", "Wet Seals"),
#  "mr4100": ("Overview", "Raw Data", "MR4100 Routine Report", "MR4100 Transient Report", "", "", "Vibration Monitoring"),
#  "mr4110": ("Overview", "Raw Data", "MR4110 Routine Report", "MR4110 Transient Report", "", "", "Vibration Monitoring")
#}
TAG_FILES = {
  "mp": "assets/files/tags.yaml", 
  "lip": "assets/files/lip-tags.yaml",
  "mr4100": "assets/files/mr4100-tags.yaml",
  "mr4110": "assets/files/mr4110-tags.yaml",
  "glycol": "assets/files/glycol-tags.yaml"
}
TAGSPEC_FILES = {
  "mp": "assets/files/tag-specs.yaml", 
  "lip": "assets/files/lip-tag-specs.yaml",
  "mr4100": "assets/files/mr4100-tag-specs.yaml",
  "mr4110": "assets/files/mr4110-tag-specs.yaml",
  "glycol": "assets/files/glycol-tag-specs.yaml"
}
MACHINES = ["mp", "lip", "mr4100", "mr4110", "glycol"]
SECOND = 60
# DEFAULT CHART STYLE
# LINE_SHAPE = 'hv'
LINE_SHAPE = 'linear'
#TIME_STRINGS = {10: '10s', 30: '30s', 60: '1m', 120: '2m', 300: '5m', 600: '10m', 1800: '30m', 0: 'Custom...'}
TIME_STRINGS = [{
    300: '5m',
    600: '10m',
    1800: '30m',
    0: 'Custom...'
}, {
    30: '30s',
    60: '1m',
    120: '2m',
    300: '5m',
    600: '10m',
    1800: '30m',
    0: 'Custom...'
}, {
    600: '10m',
    1800: '30m',
    3600: '60m',
    7200: '2h',
    14400: '4h',
    86400: '1d',
    172800: '2d',
    0: 'Custom...'
}, {
    86400: '1d',
    604800: '1w',
    1209600: '2w',
    2419200: '4w',
    4838400: '2mo',
    0: 'Custom...'
}]
# DATE TIME NOW
DATE_NOW = lambda: dt.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
DATE_NOW_IN_NS = lambda: int(DATE_NOW().strftime('%s')) * 10**9
# PIVOT OR NOT
PIVOT = True
# CHECKS LIST
CHECKS_LIST = {'none': 'None', 'nan_check': 'NaN-Check', 'overange_check': 'Overange-Check', 'irv_check': 'Instrument-Range-Validation-Check', 'deviation_check': 'Deviation-Check', 'frozen_check': 'Frozen-Check', 'roc_check': 'Rate-Of-Change-Check'}
CHECK_PERIOD = 5  # in minutes
MP_SPEED_CHECK_PERIOD = 10  # in minutes
CHECK_IRV_PERIOD = 5
SPEED_TAG = "HT_XE_2180A.PV"

# INFLUX
BUCKET = "datahub-test"
CHECK_BUCKET = "check-datahub"
ORG = "BDPOC"
# MIN NUMBER OF NAN VALUE ALLOWED: more than 118 nan samples per 2*CHECK_PERIOD minutes
MINIMUM_RATIO_NAN_ALLOW = 590 / (CHECK_PERIOD * 2 * SECOND)
#MINIMUM_RATIO_NAN_ALLOW = 118 / (CHECK_PERIOD * 2 * SECOND)
# AVAILABLE DEVIATION CHECK
AVAILABLE_DEVIATION = 2
# ROC CHECK VALUE
#ROC_CHECK_VALUE = 0.05
ROC_CHECK_VALUES = {
  "pressure": 0.1,
  "temperature": 0.05,
  "vibration": 0.3,
  "valve": 0.3,
  "flow": 0.3
}
TAG_CLASSIFIER = {
  "HT_PI": "pressure",
  "HT_PDI": "pressure",
  "HT_TI": "temperature",
  "HT_LI": "temperature",
  "HT_ZI": "vibration", 
  "HT_VI": "vibration",
  "HT_PY": "valve",
  "HT_FI": "flow"
}
# DEVIATION CHECK VALUE
DEVIATION_CHECK_VALUE = 0.05
# FROZEN CHECK VALUE
FROZEN_CHECK_VALUE = 5e-12

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

RUNNING_INDICATORS = {
  'mp': "HT_KM_2180.AND_RUNNING.OUT",
  'lip': "HT_KM_2110.AND_RUNNING.OUT",
  "mr4100": "HT_KM_4100.AND_RUNNING.OUT",
  "mr4110": "HT_KM_4110.AND_RUNNING.OUT"
}

RUL_WINDING_TEMP = {
  "HT_TI_2186A.PV": 'assets/datasets/winding-temperature/HT_TI_2186A.PV.csv',
  "HT_TI_2186C.PV": 'assets/datasets/winding-temperature/HT_TI_2186C.PV.csv',
  "HT_TI_2186E.PV": 'assets/datasets/winding-temperature/HT_TI_2186E.PV.csv'
}
