import datetime as dt
from typing import List

import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from configs.constants import CHECKS_LIST, DATE_NOW, LINE_SHAPE, PIVOT
from utils.session import sess
from dateutil import parser as dparser
from configs.logger import check_logger

def set_middle_title(chart: plotly.graph_objs.Figure, title_name, yanchor="top", xanchor="center"):
  chart.update_layout(title={
      "text": title_name,
      "y": 0.95,
      "x": 0.5,
      "xanchor": xanchor,
      "yanchor": yanchor,
  })


def draw_line_chart_by_data_frame(data, height=700, title="RAW DATA"):
  if data is None or data.empty or len(sess("tags")) == 0:
    return
  
  range_x = [
    dparser.isoparse(f'{sess("start_date")}T{sess("start_time")}+07:00'), 
    dparser.isoparse(f'{sess("end_date")}T{sess("end_time")}+07:00')
  ]
  range_y = [0, 1.1 * data["_value"].max()]
  
  chart = px.line(
    data, x="_time", y="_value", 
    labels={"_time": "Time (s)", "_value": "Value", "_field": "Tag"}, 
    color='_field', 
    line_shape=LINE_SHAPE, 
    markers=True, 
    range_x=range_x, 
    range_y=range_y
  )
  chart.update_layout(hovermode="x unified")
  csv_all = data.to_csv().encode('utf-8')
  col1, col2 = st.columns([5, 1])
  col1.subheader(title)
  col2.download_button("Download CSV", csv_all, 'all-raw.csv', 'text/csv', key="csv_all")
  st.plotly_chart(chart, use_container_width=True)

def draw_bar_chart_by_data_frame(data: pd.DataFrame) -> List[st._DeltaGenerator]:
  if data is None or data.empty:
    return
  if PIVOT and "_field" not in data.columns:
    # Convert pivot to normal dataframe
    data = pd.melt(data, id_vars=["_time", "_measurement"], value_vars=sess("tags"), value_name="_value", var_name="_field", ignore_index=False)
  range = sess("difference_time_range") if sess("time_range") == 0 else int(sess("time_range"))
  time_range_in_datetime = [DATE_NOW() - dt.timedelta(seconds=range), DATE_NOW()]
  #if sess("chart_mode") == "merge":
  chart = px.bar(
    data, 
    x="_time", y="_value", 
    labels={"_time": "Time (s)", "_value": "Value", "_field": "Tag"}, 
    color='_field', 
    range_x=time_range_in_datetime,
    height=height, 
  )
  set_middle_title(chart, CHECKS_LIST[data["_measurement"].values[0]])
  return st.plotly_chart(chart, use_container_width=True)

def draw_wet_seal_chart(data: pd.DataFrame, height=700, title="WET SEALS"):
  if data is None:
    return
  if data.empty:
    raise Exception('No data')
    #return
  range_x = [pd.to_datetime(data["_start"], errors='coerce').tolist()[0], pd.to_datetime(data["_stop"], errors='coerce').tolist()[0]]

  labels = {
    "_time": "Check At", 
    "_measurement": "Severity", 
    "_field": "Seal", 
    "dropLevel": "Drop Level (1day)", 
    "dischargeCount": "Drain count"
  }

  chart1 = px.scatter(
    data, 
    x="_time", 
    y="_field", 
    labels=labels, 
    color="_measurement",
    color_discrete_map={"Alarm": "#FF0000", "PreAlarm": "#FFA500"},
    hover_data={"dischargeCount": ':.1f', "dropLevel":":.1f"},
    height=height
  )
  
  chart1.update_layout(xaxis={'side': 'top'}, yaxis={'side': 'left'})

  csv_all = data.to_csv().encode('utf-8')

  col1, col2 = st.columns([5, 1])
  col1.subheader(title)
  col2.download_button("Download CSV", csv_all, 'all-alerts.csv', 'text/csv', key="csv_all")

  st.plotly_chart(chart1, use_container_width=True)


def draw_chart_by_check_data(data: pd.DataFrame, height=700, title="ALERT OVERVIEW", connected=False):
  if data is None:
    return
  if data.empty:
    raise Exception('No data')
    #return

  data["type"] = data.type.fillna("N/A")
  range_x = [pd.to_datetime(data["_start"], errors='coerce').tolist()[0], pd.to_datetime(data["_stop"], errors='coerce').tolist()[0]]

  hover_data={
    "type": True,
  }
  labels = {"_time": "Time (s)", "_measurement": "Alert", "_field": "Tag", "type": "IRV Alarm Type"}
  #chart = px.scatter(data, x = "_time", y = "_measurement", labels=labels, range_x = time_range_in_datetime, color = "_field", height=height)
  #st.plotly_chart(chart, use_container_width=True)

  chart1 = px.line(
    data, 
    x="_time", 
    y="_field", 
    labels=labels, 
    hover_data=hover_data,
    range_x=range_x, 
    color="_measurement", 
    symbol="type",
    height=height, 
    markers=True
  ) if connected else px.scatter(
    data, 
    x="_time", 
    y="_field", 
    labels=labels, 
    hover_data=hover_data,
    color="_measurement", 
    symbol="type",
    height=height
  )
  
  chart1.update_layout(xaxis={'side': 'top'}, yaxis={'side': 'left'})

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

  #range_x = [pd.to_datetime(data["_start"], errors='coerce').tolist()[0], pd.to_datetime(data["_stop"], errors='coerce').tolist()[0]]
  range_x = [
    dparser.isoparse(f'{sess("start_date")}T{sess("start_time")}+07:00'), 
    dparser.isoparse(f'{sess("end_date")}T{sess("end_time")}+07:00')
  ]
  range_y = [0, 1.1 * data["_value"].max()]
  labels = {"_time": "Time (s)", "_value": data["_field"][0]}

  chart1 = px.line(
    data, x="_time", y="_value", 
    labels=labels, 
    range_x=range_x, 
    range_y=range_y, 
    height=height,
    markers=True
  ) if connected else px.scatter(
    data, x="_time", y="_value", 
    range_x=range_x, 
    range_y=range_y, 
    labels=labels, 
    height=height
  )
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
  headers = [f'<b>{colName}</b>' for colName in data.columns]
  cells = [data[col].tolist() for col in data.columns]
  cellColors = [[__COLORS[cells[12][i]] for i in range(0, len(cells[0]))]] * len(cells)

  chart = go.Figure(data=[go.Table(header=dict(values=headers, height=35, font=dict(size=16)), cells=dict(values=cells, fill_color=cellColors, align=["center", "center"]))])
  chart.update_layout(height=height, margin=dict(l=0, r=0, b=0, t=30))

  irv_report = data.to_csv().encode('utf-8')
  col1, col2 = st.columns([5, 1])
  col1.subheader(f"{title}")
  col2.download_button("Download CSV", irv_report, f'{title}.csv', 'text/csv', key="irv_report")
  st.plotly_chart(chart, use_container_width=True)
  st.text_input("Conclusion:", key="conclusion", on_change="")

def draw_barchart(df, x = None, y = None, color = None, facet = None, domain = None, height=600, col_num=1, labels=None, hover_data=None):
  check_logger.info(df)
  fig = px.bar(df, x = x, y = y, color = color, facet_col=facet, facet_col_wrap=col_num,
    range_x = domain,
    text='alert_type',
    barmode='group',
    labels=labels,
    hover_data=hover_data,
    height=height, facet_row_spacing = 0.07
  )
  fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
  #fig.update_annotations(x=-0.05, textangle=-90)
  #fig.update_annotations(x=-0.05, textangle=-90)
  fig.update_yaxes(title=None)
  st.plotly_chart(fig, use_container_width=True) 

def draw_linechart(df, x = None, y = None, color = None, facet = None, domain = None, height=600, col_num=1, labels=None, hover_data=None):
  check_logger.info(df)
  fig = px.line(df, x = x, y = y, color = color, facet_col=facet, facet_col_wrap=col_num,
    range_x = domain,
    text='alert_type',
    labels=labels,
    hover_data=hover_data,
    height=height, facet_row_spacing = 0.07
  )
  fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
  #fig.update_annotations(x=-0.05, textangle=-90)
  #fig.update_annotations(x=-0.05, textangle=-90)
  fig.update_yaxes(title=None)
  st.plotly_chart(fig, use_container_width=True) 
