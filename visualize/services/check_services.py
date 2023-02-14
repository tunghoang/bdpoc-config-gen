from configs.checks import (deviation_check, frozen_check, irv_check,
                            nan_check, overange_check, roc_check)
from configs.constants import CHECK_BUCKET, ORG, CHECK_PERIOD, MINIMUM_RATIO_NAN_ALLOW
from configs.influx_client import write_api
from configs.logger import check_logger
from utils.check_utils import check_gen
from influx import InfluxWriter
import json
import pandas as pd
'''
def do_roc_check(table, devices):
  roc_checks = roc_check(table, devices)
  for point in check_gen("roc_check", roc_checks):
    InfluxWriter().setBucket(CHECK_BUCKET).write(point)
    #write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)
    check_logger.info("roc_checking 1 point")
  check_logger.info("roc_checking done")
'''

def do_deviation_check(table, deviation_checks_detail, devices):
  deviation_checks = deviation_check(table, deviation_checks_detail, devices)
  for point in check_gen("deviation_check", deviation_checks):
    InfluxWriter().setBucket(CHECK_BUCKET).write(point)
    #write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)
    check_logger.info("deviation_checking 1 point")
  check_logger.info("deviation_checking done")


def do_irv_check(table, devices, tags):
  irv_checks = irv_check(table, devices, tags)
  for point in check_gen("irv_check", irv_checks):
    InfluxWriter().setBucket(CHECK_BUCKET).write(point)
    #write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)
    check_logger.info("irv_checking 1 point")
  check_logger.info("irv_checking done")

'''
def do_frozen_check(table, devices):
  frozen_checks = frozen_check(table, devices)
  for point in check_gen("frozen_check", frozen_checks):
    InfluxWriter().setBucket(CHECK_BUCKET).write(point)
    #write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)
    check_logger.info("frozen_checking 1 point")
  check_logger.info("frozen_checking done")
'''