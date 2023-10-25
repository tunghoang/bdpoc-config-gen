import sys, warnings
from os import path
from logic_expr import detect
from influxdb_client.client.warnings import MissingPivotFunction

sys.path.append(path.join(path.dirname(__file__), "visualize"))

from visualize.configs.constants import CHECK_PERIOD, TAG_FILES
from visualize.utils.tag_utils import load_tag_config_new
from visualize.configs.logger import check_logger

from influx import Influx
warnings.simplefilter("ignore", MissingPivotFunction)

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--machine")
args = parser.parse_args()

RULE_FILES = {
  'mp': '',
  'lip': '',
  'mr4100': '',
  'mr4110': '',
  'glycol': 'assets/files/control-logic.glycol'
}

__tagFileName = TAG_FILES[args.machine.lower()]
control_logic_checks, bursty_control_logic_checks, _, _ = load_tag_config_new(__tagFileName)

df = Influx().setDebug(True).from_now(CHECK_PERIOD * 6).setRate('10s').addFields(control_logic_checks).asDataFrame()
df1 = Influx().setDebug(True).from_now(3*30*24*60).setRate(None).addFields(bursty_control_logic_checks).asDataFrame()
for event in detect(df, df1, rule_file=RULE_FILES[args.machine.lower()]):
  print("RESULT ->", event)
