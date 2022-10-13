import sys
import warnings
from os import path
from threading import Thread

import numpy as np
import pandas as pd
import schedule
from influxdb_client.client.warnings import MissingPivotFunction

sys.path.append(path.join(path.dirname(__file__), "visualize"))
from visualize.configs.constants import BUCKET, CHECK_PERIOD, ORG
from visualize.configs.influx_client import query_api
from visualize.configs.Query import Query
from visualize.services.check_services import (do_deviation_check, do_frozen_check, do_irv_check, do_nan_check, do_overange_check, do_roc_check)
from visualize.utils.tag_utils import load_tag_config

control_logic_checks, deviation_checks, devices = load_tag_config()
tags = [tag["tag_number"] for d in devices for tag in d["tags"]]
warnings.simplefilter("ignore", MissingPivotFunction)


def job():
    print("Querying ...")
    query = Query().from_bucket(BUCKET).range(f"{2 * CHECK_PERIOD}m").keep_columns("_time", "_value", "_field").aggregate_window(True).pivot("_time", "_field", "_value").to_str()
    print(query)
    table = query_api.query_data_frame(query, org=ORG).assign(_time=lambda _df: pd.to_datetime(_df['_time'], errors='coerce').astype(np.int64)).drop(columns=["result", "table", "_start", "_stop"]).set_index("_time")
    print("Query done")

    t1 = Thread(target=do_nan_check, args=(table, tags))
    interpolated_table = table.interpolate(method="linear", axis=0, limit_direction="both")
    t2 = Thread(target=do_overange_check, args=(interpolated_table, tags, devices))
    t3 = Thread(target=do_irv_check, args=(interpolated_table, tags))
    t4 = Thread(target=do_deviation_check, args=(interpolated_table, deviation_checks, devices))
    t5 = Thread(target=do_roc_check, args=(interpolated_table, devices))
    t6 = Thread(target=do_frozen_check, args=(interpolated_table, devices))

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()

    print("All Done")


# schedule.every(CHECK_PERIOD).minute.do(job)

# while True:
#     schedule.run_pending()
job()
