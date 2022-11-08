import datetime as dt
from typing import List

import numpy as np
import pandas as pd
import pytz
import streamlit as st
from configs.constants import ORG
from configs.influx_client import query_api


def get_database(query: str) -> pd.DataFrame:
  table = query_api.query_data_frame(query, org=ORG)
  # FORMAT TABLE
  # Add missing tags
  missing_tags_in_table = st.session_state["tags"] if "_field" not in table else [tag for tag in st.session_state["tags"] if tag not in table["_field"].values]
  table = pd.concat([table, pd.DataFrame({"_field": missing_tags_in_table, "_time": [table["_time"][0] for _ in missing_tags_in_table]})], join="outer", ignore_index=True)

  if "_time" in table:
    table["_time"] = table["_time"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))
    table["time_ns"] = pd.to_datetime(table["_time"], errors='coerce').astype(np.int64)

  table.set_index("time_ns", inplace=True)
  return table


def get_check(query: str) -> pd.DataFrame:
  table = query_api.query_data_frame(query, org=ORG)
  if type(table) is list:
    table = pd.concat(table)
  if table is None or table.empty:
    raise Exception("No data")
  table["_time"] = table["_time"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))
  return table


def get_tag_harvest_rate(query: str) -> float:
  table = query_api.query_data_frame(query, org=ORG)
  if table is None or table.empty:
    return 0
  return table["_value"].values[-1]


def get_check_harvest_rate(query: str) -> float:
  table = query_api.query_data_frame(query, org=ORG)
  if table is None or table.empty:
    return 0
  return table["_value"].mean()
