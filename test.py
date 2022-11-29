import sys
from os import path

import numpy as np
import pandas as pd

sys.path.append(path.join(path.dirname(__file__), "visualize"))
from visualize.configs.constants import BUCKET
from visualize.configs.influx_client import query_api
from visualize.configs.Query import Query

# query = Query().from_bucket(BUCKET).range("5m").pivot("_time", "_field", "_value").drop("_start", "_stop").to_str()
query = Query().from_bucket(BUCKET).range("5m").filter_fields(["HT_XE_2180A.PV"]).aggregate_window(True, "1m").keep_columns("_time", "_value", "_field").derivative().to_str()
table = query_api.query_data_frame(query)
table = table[(table["_value"] != 0) & (table["_value"].notna())]
# table.to_csv("new.csv")
print(table)
# table.to_csv("test.csv")
# print(table[table["_value"] > 0.05])
# table = pd.read_csv("test.csv").assign(_time=lambda _df: pd.to_datetime(_df['_time'], errors='coerce'))
# new_table = table["_value"].diff() / table["_time"].diff().dt.total_seconds()
# new_table.to_csv("test2.csv")