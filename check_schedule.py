import math
import sys
import warnings
from os import path

import numpy as np
import pandas as pd
import schedule
from influxdb_client.client.warnings import MissingPivotFunction

sys.path.append(path.join(path.dirname(__file__), "visualize"))
from visualize.configs.checks import irv_check, nan_check, overange_check
from visualize.configs.constants import BUCKET, CHECK_PERIOD, ORG
from visualize.configs.influx_client import query_api, write_api
from visualize.configs.Query import Query
from visualize.utils.tag_utils import load_tag_config

control_logic_checks, deviation_checks, devices = load_tag_config()
tags = [tag["tag_number"] for d in devices for tag in d["tags"]]
warnings.simplefilter("ignore", MissingPivotFunction)

def formater(df, measurement):
    df["_time"] = pd.to_datetime(df['_time'], errors='coerce').astype(np.int64)
    lines = [{"measurement": f"{measurement}", "tags": {"device": row["_measurement"]}, "fields": {row["_field"]: float(row["_value"])}, "time": row["_time"]} for _, row in df.iterrows() if row["_value"] != 0 and not math.isnan(row["_value"])]
    return lines

def job():
    query = Query().from_bucket(BUCKET).range(f"{2 * CHECK_PERIOD}m").keep_columns("_time", "_value", "_field", "_measurement").aggregate_window(True).to_str()
    table = query_api.query_data_frame(query, org=ORG)
    nan_checks = nan_check(table, tags).drop(columns=["_start", "_stop", "result", "table"]).pipe(formater, "nan_check")
    overange_checks = overange_check(table, tags).drop(columns=["_start", "_stop", "result", "table"]).pipe(formater, "overange_checks")
    irv_checks = irv_check(table, tags).drop(columns=["_start", "_stop", "result", "table"]).pipe(formater, "irv_checks")
    write_api.write("check-datahub", ORG, record=nan_checks)
    write_api.write("check-datahub", ORG, record=overange_checks)
    write_api.write("check-datahub", ORG, record=irv_checks)

# schedule.every(CHECK_PERIOD).minute.do(job)

# while True:
#     schedule.run_pending()
job()
