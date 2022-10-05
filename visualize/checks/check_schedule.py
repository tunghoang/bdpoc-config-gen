import datetime
import sys
from os import path
import schedule
import pandas as pd
from pandas.core.base import PandasObject

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

def formater(df, measurement):
    df["_time"] = pd.to_datetime(df['_time'], errors='coerce').astype(np.int64)
    lines = [{"measurement": f"{measurement}", "tags": {"device": row["_measurement"]}, "fields": {row["_field"]: float(row["_value"])}, "time": row["_time"]} for _, row in df.iterrows() if row["_value"] != 0 and not math.isnan(row["_value"])]
    return lines

PandasObject.formater = formater

def job():
    query = Query().from_bucket(bucket).range(f"{2 * CHECK_PERIOD}m").keep_columns("_time", "_value", "_field", "_measurement").aggregate_window(True).to_str()
    table = query_api.query_data_frame(query, org=org)
    nan_checks = nan_check(table, tags).drop(columns=["_start", "_stop", "result", "table"]).formater("nan_checks")
    overange_checks = overange_check(table, tags).drop(columns=["_start", "_stop", "result", "table"]).formater("overange_checks")
    irv_checks = irv_check(table, tags).drop(columns=["_start", "_stop", "result", "table"]).formater("irv_checks")
    write_api.write("check-datahub", org, record=nan_checks)
    write_api.write("check-datahub", org, record=overange_checks)
    write_api.write("check-datahub", org, record=irv_checks)
    return table

# schedule.every(CHECK_PERIOD).minute.do(job)

# while True:
#     schedule.run_pending()
job()
