import datetime as dt

import pytz

VIEW_MODES = ("Overview", "Raw Data", "MP Routine Report")
SECOND = 60
# DEFAULT CHART STYLE
# LINE_SHAPE = 'hv'
LINE_SHAPE = 'linear'
TIME_STRINGS = {10: '10s', 30: '30s', 60: '1m', 120: '2m', 300: '5m', 600: '10m', 1800: '30m', 0: 'Custom...'}
# DATE TIME NOW
DATE_NOW = lambda: dt.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
DATE_NOW_IN_NS = lambda: int(DATE_NOW().strftime('%s')) * 10**9
# PIVOT OR NOT
PIVOT = True
# CHECKS LIST
CHECKS_LIST = {'none': 'None', 'nan_check': 'NaN-Check', 'overange_check': 'Overange-Check', 'irv_check': 'Instrument-Range-Validation-Check', 'deviation_check': 'Deviation-Check', 'frozen_check': 'Frozen-Check', 'roc_check': 'Rate-Of-Change-Check'}
CHECK_PERIOD = 1
# INFLUX
BUCKET = "datahub"
CHECK_BUCKET = "check-datahub"
ORG = "BDPOC"
# MIN NUMBER OF NAN VALUE ALLOWED
MINIMUM_RATIO_NAN_ALLOW = 90 / (CHECK_PERIOD * 2 * SECOND)
# AVAILABLE DEVIATION CHECK
AVAILABLE_DEVIATION = 2
# ROC CHECK VALUE
ROC_CHECK_VALUE = 0.05
# DEVIATION CHECK VALUE
DEVIATION_CHECK_VALUE = 0.05
# FROZEN CHECK VALUE
FROZEN_CHECK_VALUE = 0.05

MONITORING_BUCKET = "monitoring"
CHECK_MONITORING_PERIOD = "30m"
MONITORING_PERIOD = "5m"
MONITORING_MEASUREMENT = "collector_metric"
MONITORING_FIELD = "collect_rate"
MONITORING_AGG_WINDOW = '1m'
