import datetime as dt
from typing import List

import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import streamlit as st
from configs.constants import CHECKS_LIST, DATE_NOW, LINE_SHAPE, PIVOT


def set_middle_title(chart: plotly.graph_objs.Figure, title_name):
  chart.update_layout(title={
      "text": title_name,
      "y": 0.95,
      "x": 0.5,
      "xanchor": "center",
      "yanchor": "top",
  })


def draw_line_chart_by_data_frame(data: pd.DataFrame) -> List[st._DeltaGenerator]:
  if data is None or data.empty or len(st.session_state["tags"]) == 0:
    return
  range = st.session_state["difference_time_range"] if st.session_state["time_range"] == 0 else int(st.session_state["time_range"])
  time_range_in_datetime = [DATE_NOW() - dt.timedelta(seconds=range), DATE_NOW()]
  if PIVOT:
    # Convert pivot to normal dataframe
    data = pd.melt(data, id_vars=["_time"], value_vars=st.session_state["tags"], value_name="_value", var_name="_field")
  if st.session_state["chart_mode"] == "merge":
    chart = px.line(data, x="_time", y="_value", labels={"_time": "Time (s)", "_value": "Value", "_field": "Tag"}, color='_field', line_shape=LINE_SHAPE, markers=True, range_x=time_range_in_datetime)
    return st.plotly_chart(chart, use_container_width=True)
  charts = []
  for tag in st.session_state["tags"]:
    chart = px.line(data[data["_field"] == tag], x="_time", y="_value", labels={"_time": "Time (s)", "_value": tag, "_field": "Tag"}, line_shape=LINE_SHAPE, markers=True, range_x=time_range_in_datetime)
    charts.append(st.plotly_chart(chart, use_container_width=True))
  return charts


def draw_bar_chart_by_data_frame(data: pd.DataFrame, type: str = "") -> List[st._DeltaGenerator]:
  if data is None:
    return
  if PIVOT and "_field" not in data.columns:
    # Convert pivot to normal dataframe
    data = pd.melt(data, id_vars=["_time", "_measurement"], value_vars=st.session_state["tags"], value_name="_value", var_name="_field", ignore_index=False)
  # if data.empty and type:
  #   tags = st.session_state["tags"]
  #   data = pd.DataFrame({"_measurement": [type for _ in tags], "_field": tags, "_value": [np.nan for _ in tags], "_time": [DATE_NOW() for _ in tags]})
  range = st.session_state["difference_time_range"] if st.session_state["time_range"] == 0 else int(st.session_state["time_range"])
  time_range_in_datetime = [DATE_NOW() - dt.timedelta(seconds=range), DATE_NOW()]
  if st.session_state["chart_mode"] == "merge":
    chart = px.bar(data, x="_time", y="_value", labels={"_time": "Time (s)", "_value": "Value", "_field": "Tag"}, color='_field', range_x=time_range_in_datetime)
    set_middle_title(chart, CHECKS_LIST[data["_measurement"].values[0]])
    return st.plotly_chart(chart, use_container_width=True)

  charts = []
  for tag in st.session_state["tags"]:
    chart = px.bar(data[data["_field"] == tag], x="_time", y="_value", labels={"_time": "Time (s)", "_value": data[data["_field"] == tag]["_measurement"].values[0], "_field": "Tag"}, range_x=time_range_in_datetime)
    set_middle_title(chart, tag)
    charts.append(st.plotly_chart(chart, use_container_width=True))
  return charts
