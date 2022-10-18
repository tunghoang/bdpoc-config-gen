import datetime as dt
from typing import List

import numpy as np
import pandas as pd
import pytz
import streamlit as st
from configs.constants import CHECKS_LIST, DATE_NOW, DATE_NOW_IN_NS, ORG, PIVOT
from configs.influx_client import client


def get_database(query: str) -> pd.DataFrame:
  table = pd.DataFrame()
  if not PIVOT:
    table = client.query_api().query_data_frame(query, org=ORG)
    # FORMAT TABLE
    # Add missing tags
    missing_tags_in_table = st.session_state["tags"] if "_field" not in table else [tag for tag in st.session_state["tags"] if tag not in table["_field"].values]
    table = pd.concat([pd.DataFrame({"_field": missing_tags_in_table, "_time": [table["_time"][0] for _ in missing_tags_in_table]}), table], join="outer", ignore_index=True)
    return table

  table = client.query_api().query_data_frame(query, org=ORG)

  if "_time" in table:
    table["_time"] = table["_time"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))
    table["time_ns"] = pd.to_datetime(table["_time"], errors='coerce').astype(np.int64)
  # FORMAT TABLE
  # Add missing tags
  missing_tags_in_table = [tag for tag in st.session_state["tags"] if tag not in table.columns]
  appear_tags_in_table = [tag for tag in st.session_state["tags"] if tag in table.columns]
  # Check if all tags not appear in table
  # Add blank data for all tags
  if len(appear_tags_in_table) == 0:
    table = pd.DataFrame()
    for tag in missing_tags_in_table:
      table = pd.concat([pd.DataFrame({"_measurement": st.session_state["selected_device_name"], tag: np.nan, "_time": DATE_NOW()}, index=[DATE_NOW_IN_NS()]), table], join="outer")
  else:
    # Otherwise, just add blank data for missing tags
    for tag in missing_tags_in_table:
      table[tag] = table[appear_tags_in_table[0]]
  table.set_index("time_ns", inplace=True)
  return table


def get_check(query: str) -> pd.DataFrame:
  table = client.query_api().query_data_frame(query, org=ORG)
  # table = table.groupby(["_measurement"])
  # table = [df for _, df in table]
  # Get the checks appear in each table
  # checks_appear_in_table = []
  # for idx, t in enumerate(table):
  # if not table.empty:
  #   checks_appear_in_table.append(table["_measurement"][0])
  # Get missing tags in  table (tags which have no data)
  # missing_tags_in_table = [tag for tag in st.session_state["tags"] if tag not in table["_field"].values]
  # Then add missing data to table
  # table = pd.concat([pd.DataFrame({"_field": missing_tags_in_table, "_time": [table["_time"][0] for _ in missing_tags_in_table], "_measurement": [table["_measurement"][0] for _ in missing_tags_in_table], "_value": np.nan}), table], join="outer", ignore_index=True)
  # Now format time to local time zone
  table["_time"] = table["_time"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))

  # current_checks = [st.session_state["check_mode"]]
  # # Check if needed to get all the checks
  # if st.session_state["check_mode"] == "all":
  #   current_checks = list(CHECKS_LIST.keys())[1:-1]
  # # First iterate through all checks
  # # (except the "none" and "all" flag, which located at the begin and end of the list)
  # for check in current_checks:
  #   # If the check does not appear in the table, add blank check data of all the current tags to the table
  #   if check not in checks_appear_in_table:
  #     table.append(pd.DataFrame({"_field": st.session_state["tags"], "_time": [dt.datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")) for _ in st.session_state["tags"]], "_value": [np.nan for _ in st.session_state["tags"]], "_measurement": [check for _ in st.session_state["tags"]]}))
  return table


def execute(query: str) -> float:
  table = client.query_api().query_data_frame(query, org=ORG)
  if table is None or table.empty:
    return 0.
  return table.iloc[-1, 6]
