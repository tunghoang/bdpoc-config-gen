import datetime as dt
from typing import List

import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from configs.constants import CHECKS_LIST, DATE_NOW, LINE_SHAPE, PIVOT


def set_middle_title(chart: plotly.graph_objs.Figure, title_name, yanchor="top", xanchor="center"):
  chart.update_layout(title={
      "text": title_name,
      "y": 0.95,
      "x": 0.5,
      "xanchor": xanchor,
      "yanchor": yanchor,
  })


def draw_line_chart_by_data_frame(data: pd.DataFrame) -> List[st._DeltaGenerator]:
  if data is None or data.empty or len(st.session_state["tags"]) == 0:
    return
  range_x = [data["_start"].values[0], data["_stop"].values[0]]
  if st.session_state["chart_mode"] == "merge":
    range_y = [0, 1.1 * data["_value"].max()]
    chart = px.line(data, x="_time", y="_value", labels={"_time": "Time (s)", "_value": "Value", "_field": "Tag"}, color='_field', line_shape=LINE_SHAPE, markers=True, range_x=range_x, range_y=range_y)
    return st.plotly_chart(chart, use_container_width=True)
  charts = []
  st.write(data)
  for tag in st.session_state["tags"]:
    if tag in data["_field"].values:
      draw_data = data[data["_field"] == tag]
      range_y = [0, 1.1 * draw_data["_value"].max()]
      chart = px.line(draw_data, x="_time", y="_value", labels={"_time": "Time (s)", "_value": tag, "_field": "Tag"}, line_shape=LINE_SHAPE, markers=True, range_x=range_x, range_y=range_y)
      charts.append(st.plotly_chart(chart, use_container_width=True))
  return charts


def draw_bar_chart_by_data_frame(data: pd.DataFrame, type: str = "") -> List[st._DeltaGenerator]:
  if data is None or data.empty:
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


def draw_chart_by_check_data(data: pd.DataFrame, height=700, title="ALERT OVERVIEW", connected=False):
  if data is None:
    return
  if data.empty:
    raise Exception('No data')
    #return
  print("draw_chart_by_check")
  #print(data["_start"])
  print(data["_start"].tolist()[0])
  range_x = [pd.to_datetime(data["_start"], errors='coerce').tolist()[0], pd.to_datetime(data["_stop"], errors='coerce').tolist()[0]]
  
  labels = {"_time": "Time (s)", "_measurement": "Alert", "_field": "Tag"}
  #chart = px.scatter(data, x = "_time", y = "_measurement", labels=labels, range_x = time_range_in_datetime, color = "_field", height=height)
  #st.plotly_chart(chart, use_container_width=True)

  chart1 = px.line(data, x="_time", y="_field", labels=labels, range_x=range_x, color="_measurement", height=height, markers=True) if connected else px.scatter(data, x="_time", y="_field", labels=labels, color="_measurement", height=height)
  chart1.update_layout(xaxis={'side': 'top'})

  csv_all = data.to_csv().encode('utf-8')

  col1, col2 = st.columns([5, 1])
  col1.subheader(title)
  col2.download_button("Download CSV", csv_all, 'all-alerts.csv', 'text/csv', key="csv_all")

  st.plotly_chart(chart1, use_container_width=True)


def draw_chart_by_raw_data(data: pd.DataFrame, height=700, title="RAW DATA", connected=False):
  if data is None:
    return
  if data.empty:
    raise Exception('No data')

  range_x = [pd.to_datetime(data["_start"], errors='coerce').tolist()[0], pd.to_datetime(data["_stop"], errors='coerce').tolist()[0]]
  print(range_x)
  range_y = [0, 1.1 * data["_value"].max()]
  labels = {"_time": "Time (s)", "_value": data["_field"][0]}

  chart1 = px.line(data, x="_time", y="_value", labels=labels, range_x=range_x, range_y=range_y, height=height, markers=True) if connected else px.scatter(data, x="_time", y="_value", range_x=range_x, range_y=range_y, labels=labels, height=height)
  chart1.update_layout(xaxis={'side': 'top'})

  csv_tag_raw = data.to_csv().encode('utf-8')

  col1, col2 = st.columns([5, 1])
  col1.markdown(f"#### _Raw data_")
  col2.download_button("Download CSV", csv_tag_raw, f'{title}.csv', 'text/csv', key="csv_tag_raw")

  st.plotly_chart(chart1, use_container_width=True)

__COLORS = ["#fffff8", "#ffeeee", "#ffaaaa", "#ff8888"]

def conclusion_change():
  pass

def draw_table(data: pd.DataFrame, height=700, title=""):
  #headers = data.columns.tolist()
  headers = [ f'<b>{colName}</b>' for colName in data.columns ]
  cells = [ data[col].tolist() for col in data.columns ]
  cellColors = [ [ __COLORS[cells[12][i]] for i in range(0, len(cells[0]))  ] ] * len(cells)
  
  chart = go.Figure( data = [
    go.Table( 
      header=dict(values=headers, height=35, font=dict(size=16)), 
      cells=dict(
        values=cells, 
        fill_color=cellColors,
        align=["center", "center"]
      )    
    )
  ] )
  chart.update_layout(height = height, margin=dict(l=0,r=0,b=0,t=30))
  
  irv_report = data.to_csv().encode('utf-8')
  col1, col2 = st.columns([5, 1])
  col1.subheader(f"{title}")
  col2.download_button("Download CSV", irv_report, f'{title}.csv', 'text/csv', key="irv_report")
  st.plotly_chart(chart, use_container_width=True)
  st.text_input("Conclusion:", key="conclusion", on_change="")
  