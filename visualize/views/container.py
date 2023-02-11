import json
from datetime import timedelta
from itertools import islice

import dateutil.parser as parser
import numpy as np
import pandas as pd
import pytz
import streamlit as st
from configs.constants import (BUCKET, INFINITIES, LABELS, ORG, START_DERIVATIVE_VALUE, STOP_DERIVATIVE_VALUE, TIME_STRINGS)
from configs.custom_components import outstanding_tag_list, st_custom_dataframe
from configs.influx_client import query_api
from configs.query import Query
from utils.draw_chart import (draw_chart_by_check_data, draw_chart_by_raw_data, draw_table)
from utils.influx_utils import query_irv_transient_tags
from utils.session import sess, update_session
from utils.tag_utils import load_tag_specs
from utils.view_utils import (get_device_by_name, select_tag_update_calldb, visualize_data_by_raw_data)


def render_overview():
  draw_chart_by_check_data(sess("data"))


def inside(v, b1, b2):
  if b1 is None:
    b1 = 0
  if b2 is None:
    b2 = 0
  return (v - b1) * (v - b2) < 0


attributes = ["low3", "low2", "low", "high", "high2", "high3"]


def irv_diagnose(min_max, tagSpec, tag):
  if tagSpec is None:
    return "NA", ""
  if all([(tagSpec[a] == "NA") for a in attributes]):
    return "NA", ""
  print(tag, tagSpec)
  shutdown_limits = [tagSpec["low3"], tagSpec["high3"]]
  alarm_limits = [tagSpec["low2"], tagSpec["high2"]]
  prealarm_limits = [tagSpec["low"], tagSpec["high"]]

  # results = dict(shutdowns = [False, False], alarms = [False, False], prealams = [False, False], normals = [False, False])
  flags = [0, 0]
  output = ""

  for i in range(0, 2):
    if inside(min_max[i], INFINITIES[i], shutdown_limits[i]):
      if shutdown_limits[i] != alarm_limits[i]:
        flags[i] = 3
        comment = f"{LABELS[i]} - SHUTDOWN;"
      elif alarm_limits[i] != prealarm_limits[i]:
        flags[i] = 2
        comment = f"{LABELS[i]} - ALARM;"
      else:
        flags[i] = 1
        comment = f"{LABELS[i]} - PREALARM;"
      output = output + comment
    elif inside(min_max[i], shutdown_limits[i], alarm_limits[i]):
      # results["alarms"][i] = True
      flags[i] = 2
      output = output + f"{LABELS[i]} - ALARM;"
    elif inside(min_max[i], alarm_limits[i], prealarm_limits[i]):
      # results["prealarms"][i] = True
      flags[i] = 1
      output = output + f"{LABELS[i]} - PREALARM;"
    elif inside(min_max[i], prealarm_limits[0], prealarm_limits[1]):
      # results["normals"][i] = True
      flags[i] = 0
      output = output + f"{LABELS[i]} - NORMAL;"
  return max(flags[0], flags[1]), output


def __irvTable(df, header="", withSearch=False, withComment=False, withDownload=False, key=0):
  tagDict = load_tag_specs()
  df = (df.groupby("_field", as_index=False)._value.agg({"Min": lambda x: min(list(x)), "Max": lambda x: max(list(x))}))

  df[["Group", "Description", "Unit", "LLL", "LL", "L", "H", "HH", "HHH", "Flag", "Evaluation"]] = df.apply(lambda row: pd.Series([
      tagDict.get(row["_field"], {}).get("device", "NA"),
      tagDict.get(row["_field"], {}).get("description", "NA"),
      tagDict.get(row["_field"], {}).get("unit", "NA"),
      tagDict.get(row["_field"], {}).get("low3", "NA"),
      tagDict.get(row["_field"], {}).get("low2", "NA"),
      tagDict.get(row["_field"], {}).get("low", "NA"),
      tagDict.get(row["_field"], {}).get("high", "NA"),
      tagDict.get(row["_field"], {}).get("high2", "NA"),
      tagDict.get(row["_field"], {}).get("high3", "NA"), *irv_diagnose((row["Min"], row["Max"]), tagDict.get(row["_field"], None), row["_field"])
  ]),
                                                                                                            axis=1)

  df.rename(columns={"_field": "Field"}, inplace=True)

  df = df.sort_values("Group")
  records = df.to_dict("records")
  # draw_table(df, height=700, title="MP Routing Monitoring")
  st_custom_dataframe(data=records, header=header, withSearch=withSearch, withComment=withComment, withDownload=withDownload, key=key)


def render_irv_report():
  if sess("data") is not None:
    df = sess("data")[["_field", "_value"]]
    __irvTable(df, header="MP Routing Monitoring", withSearch=True, withComment=True, withDownload=True)


def render_mp_transient_report():
  st.subheader("MP transient report")
  if sess("data") is not None:
    sess("data")

    if sess("data").empty:
      return st.markdown("<h3 class='no-mp-data'>No stop and start period</h3>", unsafe_allow_html=True)
    for idx, row in sess("data").iterrows():
      startTime = parser.isoparse(row["start"])
      length = 5 if row["_field"] == "shutdown" else 10
      print(length)
      stopTime = startTime + timedelta(minutes=length)
      df = query_irv_transient_tags(startTime, stopTime)
      header = {
          "alert_type": "STOP" if row["_field"] == "shutdown" else "START",
          "start": str(startTime),
          "end": str(stopTime),
      }
      __irvTable(df, header=header, key=idx)


def render_roc_report():
  st.subheader("MP Startup report")
  if sess("data") is not None:
    if sess("data").empty:
      return st.markdown("<h3 class='no-mp-data'>No stop and start period</h3>", unsafe_allow_html=True)
    #df = sess("data.sort_values("_time")")
    groups = sess("data").groupby("group")
    for name, group in groups:
      print(group)
      print("............")
      start = group["_start"].tolist()[0].strftime("%Y-%m-%d %H:%M:%S")
      end = group["_stop"].tolist()[0].strftime("%Y-%m-%d %H:%M:%S")

      header = {
          "alert_type": "START" if group["sign"].tolist()[0] > 0 else "STOP",
          "start": start,
          "end": end,
      }
      header = json.dumps(header)
      __irvTable(group, header=header, key=name)


def render_roc_report_old():
  tagDict = load_tag_specs()
  if sess("data") is not None:
    df = sess("data").sort_values("_time")
    df.to_csv("temp.csv")
    tables = sess("data").groupby("_field")
    iters = None
    for _idx, table in tables:
      table = table.reset_index()
      iters = table.iterrows()
      st.subheader(f"{_idx}")
      for idx, row in iters:
        start = idx
        end = None
        alert_type = None
        for i in range(idx + 1, len(table)):
          if row["derivative"] >= START_DERIVATIVE_VALUE:
            if table.at[i, "derivative"] < START_DERIVATIVE_VALUE:
              end = i
              alert_type = "START"
              next(islice(iters, end - start - 1, end - start + 1))
              break
          elif row["derivative"] <= -STOP_DERIVATIVE_VALUE:
            if table.at[i, "derivative"] > -STOP_DERIVATIVE_VALUE:
              end = i
              alert_type = "STOP"
              next(islice(iters, end - start - 1, end - start + 1))
              break
        if end is not None:
          df = table[start:end][["_field", "_value"]]

          df = (df.groupby("_field", as_index=False)["_value"].agg({"Min": lambda x: min(list(x)), "Max": lambda x: max(list(x))}))

          df[["Group", "Description", "Unit", "LLL", "LL", "L", "H", "HH", "HHH", "Flag", "Evaluation"]] = df.apply(lambda row: pd.Series([
              tagDict.get(row["_field"], {}).get("device", "NA"),
              tagDict.get(row["_field"], {}).get("description"),
              tagDict.get(row["_field"], {}).get("unit", "NA"),
              tagDict.get(row["_field"], {}).get("low3", "NA"),
              tagDict.get(row["_field"], {}).get("low2", "NA"),
              tagDict.get(row["_field"], {}).get("low", "NA"),
              tagDict.get(row["_field"], {}).get("high", "NA"),
              tagDict.get(row["_field"], {}).get("high2", "NA"),
              tagDict.get(row["_field"], {}).get("high3", "NA"), *irv_diagnose((row["Min"], row["Max"]), tagDict.get(row["_field"], None))
          ]),
                                                                                                                    axis=1)

          df.rename(columns={"_field": "Field"}, inplace=True)

          df = df.sort_values("Group")
          records = df.to_dict("records")
          # print(records)
          # draw_table(df, height=700, title="MP Routing Monitoring")
          header = {
              "alert_type": alert_type,
              "start": table.at[start, "_time"].strftime("%Y-%m-%d %H:%M:%S"),
              "end": table.at[end, "_time"].strftime("%Y-%m-%d %H:%M:%S"),
          }
          header = json.dumps(header)
          st_custom_dataframe(data=records, header=header, key=f"{_idx}.{start}.{end if end is not None else 0}")


def render_columns(devices, deviation_checks):
  print('render columns')
  col1, col2 = st.columns([1.5, 6])
  with col1:
    selected_device = get_device_by_name(devices, sess("selected_device_name"))
    tags = selected_device["tags"] if selected_device is not None else []
    tags = filter(lambda tag: sess("search_tags").lower() in tag["tag_number"].lower(), tags)
    for tag in tags:
      st.checkbox(
          tag["tag_number"],
          True if tag["tag_number"] in sess("tags") else False,
          on_change=select_tag_update_calldb,
          args=(tag["tag_number"]),
      )

  with col2:
    st.write(sess("tags"))
    # st.write(st.session_state)

    if sess("view_mode") > 0:
      visualize_data_by_raw_data()


def render_outstanding_tags(container):
  if sess("data") is None:
    return
  print('render_outstanding_tags')
  df = sess("data").drop_duplicates(subset=['_measurement', '_field'], keep='last')[['_field', '_measurement', '_time']]
  df = df.pivot(index='_field', columns='_measurement')
  df = df['_time'].reset_index()
  df.columns.name = None

  _nTags = df['_field'].count()

  with container.container():
    st.markdown('''<div
      class="streamlit-expanderHeader st-ae st-bw st-ag st-ah st-ai st-aj st-bx st-by st-bz st-c0 st-c1 st-c2 st-c3 st-ar st-as st-c4 st-c5 st-b3 st-c6 st-c7 st-c8 st-b4 st-c9 st-ca st-cb st-cc st-cd"
      style="background:white;">⚙ 💗 🔥 OUTSTANDING TAGS</div>
    ''',
                unsafe_allow_html=True)
    nMasks = list(map(lambda x: pd.isnull(x), df['nan_check'].tolist())) if 'nan_check' in df.columns else [True] * _nTags
    oMasks = list(map(lambda x: pd.isnull(x), df['overange_check'].tolist())) if 'overange_check' in df.columns else [True] * _nTags
    iMasks = list(map(lambda x: pd.isnull(x), df['irv_check'].tolist())) if 'irv_check' in df.columns else [True] * _nTags
    fMasks = list(map(lambda x: pd.isnull(x), df['frozen_check'].tolist())) if 'frozen_check' in df.columns else [True] * _nTags
    print(df.columns)
    print(fMasks)
    #print(df['frozen_check'])

    tags = df["_field"].tolist()
    tagDict = load_tag_specs()

    selected_check_indices = outstanding_tag_list("Dummy", tags=tags, tagDescriptions=[tagDict.get(tag, {}).get('description', "") for tag in tags], nMasks=nMasks, oMasks=oMasks, iMasks=iMasks, fMasks=fMasks)
    try:
      update_session("_selected_tag", None)
      update_session("_selected_checks", [])
      if selected_check_indices['nIdx'] >= 0:
        update_session("_selected_tag", df['_field'][selected_check_indices['nIdx']])
        sess("_selected_checks").append('nan_check')

      if selected_check_indices['oIdx'] >= 0:
        update_session("_selected_tag", df['_field'][selected_check_indices['oIdx']])
        sess("_selected_checks").append('overange_check')

      if selected_check_indices['iIdx'] >= 0:
        update_session("_selected_tag", df['_field'][selected_check_indices['iIdx']])
        sess("_selected_checks").append('irv_check')

      if selected_check_indices['fIdx'] >= 0:
        update_session("_selected_tag", df['_field'][selected_check_indices['fIdx']])
        sess("_selected_checks").append('frozen_check')

    except:
      pass


def getRange(data):
  start = pd.to_datetime(data["_start"], errors='coerce').astype(np.int64).tolist()[0] // 10**9
  stop = pd.to_datetime(data["_stop"], errors='coerce').astype(np.int64).tolist()[0] // 10**9
  return (start, stop)


def render_inspection():
  df = sess("data")
  df = df[(df["_field"] == sess("_selected_tag"))][['_time', '_field', "_value", '_measurement']]
  for check in sess("_selected_checks"):
    df1 = df[df['_measurement'] == check]
    st.markdown(f"#### _{check}_")
    st.write(df1)
  time_range_settings = TIME_STRINGS[sess('view_mode')]
  time = f"{int(sess('difference_time_range'))}s" if sess("time_range") == 0 else time_range_settings[sess('time_range')]
  startStr, stopStr = getRange(sess("data"))

  query = Query().from_bucket(BUCKET).range1(startStr, stopStr).filter_fields(sess("_selected_tag")).keep_columns("_time", "_value", "_field").aggregate_window(True).to_str()

  raw_data = query_api.query_data_frame(query, org=ORG)
  # print(raw_data)
  raw_data["_time"] = raw_data["_time"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))
  raw_data["_start"] = raw_data["_start"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))
  raw_data["_stop"] = raw_data["_stop"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))

  if raw_data is not None:
    draw_chart_by_raw_data(raw_data, height=450, title=sess("_selected_tag"), connected=True)
