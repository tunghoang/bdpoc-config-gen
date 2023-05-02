import sys
import time
import warnings
import traceback

import argparse

from os import path
from threading import Thread

from dateutil import parser as dparser
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from influxdb_client.client.warnings import MissingPivotFunction

sys.path.append(path.join(path.dirname(__file__), "visualize"))
from configs.query import Query

from visualize.configs.constants import (BUCKET, CHECK_PERIOD, MONITORING_BUCKET, ORG)
from visualize.configs.influx_client import query_api, write_api
from visualize.configs.logger import check_logger

from visualize.checks.nan_check import do_nan_check
from visualize.checks.overange_check import do_overange_check
from visualize.checks.roc_check import do_roc_check

from visualize.services.check_services import (do_deviation_check, do_irv_check)
from visualize.utils.tag_utils import load_tag_config
from influx import Influx

control_logic_checks, deviation_checks, devices = load_tag_config()
tags = [tag["tag_number"] for d in devices for tag in d["tags"]]
warnings.simplefilter("ignore", MissingPivotFunction)

def process(table, interpolated_table):
  #do_nan_check(table, tags)
  #do_overange_check(interpolated_table, tags, devices)
  #do_irv_check(interpolated_table, devices, tags)
  do_roc_check(interpolated_table)
  '''
  do_deviation_check(interpolated_table, deviation_checks, devices)
  do_frozen_check(interpolated_table, devices)'''
def processParallel(table, interpolated_table):
  t1 = Thread(target=do_nan_check, args=(table, tags))
  t2 = Thread(target=do_overange_check, args=(interpolated_table, tags, devices))
  #t3 = Thread(target=do_irv_check, args=(interpolated_table, devices, tags))
  #t4 = Thread(target=do_deviation_check, args=(interpolated_table, deviation_checks, devices))
  t5 = Thread(target=do_roc_check, args=(interpolated_table, ))
  #t6 = Thread(target=do_frozen_check, args=(interpolated_table, devices))

  t1.start()
  t2.start()
  #t3.start()
  #t4.start()
  t5.start()
  #t6.start()

  t1.join()
  t2.join()
  #t3.join()
  #t4.join()
  t5.join()
  #t6.join()
  write_api.write(MONITORING_BUCKET, ORG, {"measurement": "check_harvest", "fields": {"rate": 1.0}})
  print("All Done")
  
def job():
  print("Querying ...")
  
  instance = Influx().from_now(2 * CHECK_PERIOD).addFields(tags)
  table = instance.setInterpolation(False).asPivotDataFrame()
  interpolated_table = instance.setInterpolation(True).setRate('2s').asPivotDataFrame()
  print("Query done")
  processParallel(table, interpolated_table)
  
def job1(startTime, stopTime):
  instance = Influx().setStart(startTime).setStop(stopTime).addFields(tags)
  table = instance.setInterpolation(False).asPivotDataFrame()
  interpolated_table = instance.setInterpolation(True).setRate('2s').asPivotDataFrame()
  
  print("Query done")
  processParallel(table, interpolated_table)

parser = argparse.ArgumentParser(prog = "Check MP manual", description="Check MP Manual", epilog="")
parser.add_argument("--start")
parser.add_argument("--end")

args = parser.parse_args()

try:
  startTime = dparser.isoparse(args.start)
  endTime = dparser.isoparse(args.end)
  while startTime.timestamp() < endTime.timestamp():
    stopTime = startTime + timedelta(minutes = 10 * CHECK_PERIOD)
    job1(startTime, stopTime)
    startTime = stopTime
    time.sleep(0.5)
except:
  traceback.print_exc()
  print("Wrong date time format")
  exit(-1)
