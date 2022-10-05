import sys
from os import path
import schedule
import pandas as pd
import math
import numpy as np

sys.path.append(path.join(path.dirname(__file__), ".."))
from checks import nan_check, overange_check, irv_check
from configs.constants import CHECK_PERIOD
from Query import Query
from utils.tag_utils import load_tag_config
from configs.constants import BUCKET, ORG
from configs.influx_client import write_api, query_api

control_logic_checks, deviation_checks, devices = load_tag_config()
tags = [tag["tag_number"] for d in devices for tag in d["tags"]]

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
    return table

schedule.every(CHECK_PERIOD).minute.do(job)

while True:
    schedule.run_pending()
