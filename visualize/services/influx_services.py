import numpy as np
import pandas as pd
import streamlit as st
from configs.constants import ORG
from configs.influx_client import client


def get_database_by_table_mode(table_mode: str, query: str) -> pd.DataFrame:
  if table_mode == "thin":
    table = client.query_api().query_data_frame(query, org=ORG)
    if table.empty:
      return pd.DataFrame()
    # FORMAT TABLE
    # Add missing tags
    no_data_tags = [tag for tag in st.session_state["tags"] if tag not in table["_field"].values]
    missing_tags_df = pd.DataFrame({"_field": no_data_tags, "_time": [table["_time"][0] for _ in no_data_tags]})
    return pd.concat([missing_tags_df, table], join="outer")
  elif table_mode == "fat":
    table = client.query_api().query_data_frame(query, org=ORG)
    if table.empty:
      return pd.DataFrame()
    # FORMAT TABLE
    # Add missing tags
    no_data_tags = [tag for tag in st.session_state["tags"] if tag not in table.columns]
    has_data_tags = [tag for tag in st.session_state["tags"] if tag in table.columns]
    for tag in no_data_tags:
      table[tag] = table[has_data_tags[0]] = np.nan
    return table


def get_check(query: str) -> pd.DataFrame:
  table = client.query_api().query_data_frame(query, org=ORG)
  if type(table) == pd.DataFrame:
    if "_time" not in table:
      return pd.DataFrame()
  return table
