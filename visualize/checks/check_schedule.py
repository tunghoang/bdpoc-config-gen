import datetime
import sys
from os import path
import schedule
import pandas as pd

sys.path.append(path.join(path.dirname(__file__), ".."))
from influx_utils import *
from checks import *
from constants import *
from Query import Query
from config_utils import cfg_load_tag_config
from configs.influx_client import client, bucket, org, write_api, query_api

control_logic_checks, deviation_checks, devices = cfg_load_tag_config()
tags = [tag["tag_number"] for d in devices for tag in d["tags"]]

current_data = pd.DataFrame()

def job():
    query = Query().from_bucket(bucket).range(f"{2 * CHECK_PERIOD}m").keep_columns("_time", "_value", "_field").aggregate_window(True).to_str()
    table = query_api.query_data_frame(query, org=org)
    nan_checks = nan_check_multi(table, tags).drop(columns=["_start", "_stop", "result", "table"]).set_index("_time")
    nan_checks.to_csv("nan_checks.csv")
    write_api.write("check-datahub", org, record=nan_checks, data_frame_measurement_name="nan_checks")
    return table

# schedule.every(CHECK_PERIOD).minute.do(job)

# while True:
#     schedule.run_pending()
job()
