import sys
from operator import itemgetter
from os import path
from queue import LifoQueue

import numpy as np
import pandas as pd
import yaml

sys.path.append(path.join(path.dirname(__file__), "visualize"))
from configs.query import Query

from visualize.configs.constants import BUCKET, CHECK_PERIOD, ORG
from visualize.configs.influx_client import query_api
from visualize.utils.influx_utils import check_status

with open("test.yaml", "r") as yaml_file:
  control_logic_checks = itemgetter("control_logic_checks")(yaml.safe_load(yaml_file))


def random():
  query = Query().from_bucket(BUCKET).range(f"{2 * CHECK_PERIOD}m").keep_columns("_time", "_field", "_value").aggregate_window(True).pivot("_time", "_field", "_value").to_str()
  table = query_api.query_data_frame(query, org=ORG).assign(_time=lambda _df: pd.to_datetime(_df['_time'], errors='coerce').astype(np.int64)).drop(columns=["result", "table", "_start", "_stop"]).set_index("_time")
  table = table.interpolate(method="linear", axis=0, limit_direction="both")
  new_table = pd.DataFrame()
  new_table["_time"] = table.index
  new_table["HT_PDI_2181.PV"] = table["HT_FI_2188.PV"].values
  new_table["HT_SDV_2181_GSC.PV"] = [np.random.randint(0, 2) for _ in table.index]
  new_table["HT_SDV_2181_GSO.PV"] = [np.random.randint(0, 2) for _ in table.index]
  return new_table


# random().to_csv("test.csv")

table = pd.read_csv("test.csv")
for clc in control_logic_checks:
  if clc["variable"] in table.columns and all(depend in table.columns for depend in clc["depend"]["items"]):
    checks = []
    for idx, row in table.iterrows():
      params = [row[dp] for dp in clc["depend"]["items"]]
      for rule, params_rule in clc["depend"]["rules"].items():
        if params == params_rule:
          if idx > 1 and "state" in table.columns:
            if table.at[idx - 1, "state"] == "Open" and rule == "Close" and row[clc["variable"]] > table.at[idx - 1, clc["variable"]]:
              checks.append({idx: "Close rule failed"})
            elif table.at[idx - 1, "state"] == "Close" and rule == "Open" and row[clc["variable"]] < table.at[idx - 1, clc["variable"]]:
              checks.append({idx: "Open rule failed"})
            elif rule == "Error":
              checks.append({idx: "Error"})
            elif rule == "Travelling":
              if idx > 4:
                if table[idx - 4:idx][table[idx - 4:idx]["state"] == "Travelling"].count()[clc["variable"]] == 4:
                  checks.append({idx: "Travelling error"})
          table.at[idx, "state"] = rule
print(checks)
