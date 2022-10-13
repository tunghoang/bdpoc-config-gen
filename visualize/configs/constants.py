import datetime as dt

import pytz

SECOND = 60
# DEFAULT CHART STYLE
LINE_SHAPE = 'hv'
# LINE_SHAPE = 'linear'
TIME_STRINGS = {'10': '10s', '30': '30s', '60': '1m', '120': '2m', '300': '5m', '600': '10m', '1800': '30m', '0': 'Custom...'}
# DATE TIME NOW
DATE_NOW = lambda: dt.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
# CHECKS LIST
CHECKS_LIST = {"NaN-Check": "nan", "Overange-Check": "overange", "Instrument-Range-Validation-Check": "irv"}
CHECK_PERIOD = 1
# INFLUX
BUCKET = "datahub"
CHECK_BUCKET = "check-datahub"
ORG = "BDPOC"
# MIN NUMBER OF NAN VALUE ALLOWED
MINIMUM_RATIO_NAN_ALLOW = 90 / (CHECK_PERIOD * 2 * SECOND)
# AVAILABLE DEVIATION CHECK
AVAILABLE_DEVIATION = 2
