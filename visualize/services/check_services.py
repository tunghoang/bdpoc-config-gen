from configs.checks import (deviation_check, frozen_check, irv_check, nan_check, overange_check, roc_check)
from configs.constants import CHECK_BUCKET, ORG
from configs.influx_client import write_api
from utils.check_utils import check_gen


def do_roc_check(table, devices):
    roc_checks = roc_check(table, devices)
    for point in roc_checks:
        write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)


def do_deviation_check(table, deviation_checks_detail):
    deviation_checks = deviation_check(table, deviation_checks_detail)
    for point in deviation_checks:
        write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)


def do_irv_check(table, tags):
    irv_checks = irv_check(table, tags, True)
    for point in check_gen("irv_check", irv_checks):
        write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)


def do_overange_check(table, tags):
    overange_checks = overange_check(table, tags, True)
    for point in check_gen("overange_check", overange_checks):
        write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)


def do_nan_check(table, tags):
    nan_checks = nan_check(table, tags, True)
    for point in check_gen("nan_check", nan_checks):
        write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)


def do_frozen_check(table, devices):
    frozen_checks = frozen_check(table, devices)
    for point in frozen_checks:
        write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)
