import numpy as np
import pandas as pd
import pytz
import streamlit as st
from configs.constants import BUCKET, CHECKS_LIST, ORG, TIME_STRINGS
from configs.influx_client import query_api
from configs.Query import Query
from utils.draw_chart import draw_chart_by_check_data, draw_chart_by_raw_data, draw_table
from utils.session import update_interpolated_calldb_session
from utils.tag_utils import load_tag_specs
from utils.view_utils import (cal_different_time_range, get_device_by_name, select_tag_update_calldb, visualize_data_by_raw_data)


# def render_configurations():
#   with st.expander("SETTINGS", True):
#     if st.session_state["time_range"] == 0:
#       start_date, end_date = st.columns([1, 1])
#       with start_date:
#         st.date_input("Start Date", value=st.session_state["start_time"], key="start_date", on_change=cal_different_time_range)
#       with end_date:
#         st.date_input("End Date", value=st.session_state["end_time"], key="end_date", on_change=cal_different_time_range)
#     tCols = st.columns([1, 1, 1, 1, 1, 1])
#     with tCols[0]:
#       # Check if raw_data is True, user can view raw data
#       st.selectbox("Check", CHECKS_LIST.keys() if st.session_state["raw_data"] else list(CHECKS_LIST.keys())[1:], format_func=lambda check_mode: CHECKS_LIST[check_mode], key="check_mode", disabled=st.session_state["raw_data"])
#     with tCols[1]:
#       st.selectbox("Preprocessing", (True, False), index=0 if st.session_state["interpolated"] else 1, format_func=lambda interpolated: "Interpolated" if interpolated else "Raw", on_change=update_interpolated_calldb_session, disabled=not st.session_state["raw_data"])
#     with tCols[2]:
#       st.selectbox("Time Range", options=TIME_STRINGS.keys(), format_func=lambda sec: TIME_STRINGS[sec], key="time_range")
#     with tCols[3]:
#       st.selectbox("Fill missing data", ("NaN", "Last"), key="missing_data", disabled=not st.session_state["raw_data"])
#     with tCols[4]:
#       st.selectbox("Chart Style", ("all", "merge"), key="chart_mode")
#     with tCols[5]:
#       st.selectbox("Raw data", (True, False), key="raw_data")


def render_overview():
  draw_chart_by_check_data(st.session_state["data"])

def inside(v, b1, b2):
  return (v - b1) * (v - b2) < 0

__INFINITIES = (-999999.0, 999999.0)
__LABELS = ("LOW", "HIGH")

def irv_diagnose(min_max, tagSpec):
  if tagSpec is None: 
    return ""

  shutdown_limits = [tagSpec["low3"], tagSpec["high3"]]
  alarm_limits = [tagSpec["low2"], tagSpec["high2"]]
  prealarm_limits = [tagSpec["low"], tagSpec["high"]]
  
  # results = dict(shutdowns = [False, False], alarms = [False, False], prealams = [False, False], normals = [False, False])
  flags = [0, 0]
  output = ""
  
  for i in range(0, 2):
    if inside(min_max[i], __INFINITIES[i], shutdown_limits[i]):
      if shutdown_limits[i] != alarm_limits[i]:
        flags[i] = 3
        comment = f"{__LABELS[i]} - SHUTDOWN;"
      elif alarm_limits[i] != prealarm_limits[i]:
        flags[i] = 2
        comment = f"{__LABELS[i]} - ALARM;"
      else:
        flags[i] = 1
        comment = f"{__LABELS[i]} - PREALARM;"
      output = output + comment
    elif inside(min_max[i], shutdown_limits[i], alarm_limits[i]):
      # results["alarms"][i] = True
      flags[i] = 2
      output = output + f"{__LABELS[i]} - ALARM;"
    elif inside(min_max[i], alarm_limits[i], prealarm_limits[i]):
      # results["prealarms"][i] = True
      flags[i] = 1
      output = output + f"{__LABELS[i]} - PREALARM;"
    elif inside(min_max[i], prealarm_limits[0], prealarm_limits[1]):
      # results["normals"][i] = True
      flags[i] = 0
      output = output + f"{__LABELS[i]} - NORMAL;"
  return max(flags[0], flags[1]), output
  
def render_irv_report():
  tagDict = load_tag_specs()
  if st.session_state.data is not None:
    df = st.session_state.data[["_field", "_value"]]
      
    df = (df.groupby("_field", as_index=False)._value.agg({"Min": lambda x: min(list(x)), "Max": lambda x: max(list(x))}))
    
    df[[ "Group",
         "Description",
         "Unit", 
         "LLL", 
         "LL",
         "L","H",
         "HH",
         "HHH",
         "Flag", "Evaluation"]] = df.apply(lambda row: pd.Series([ tagDict.get(row["_field"], {}).get("device", "NA"),
                                                  tagDict.get(row["_field"], {}).get("description"),
                                                  tagDict.get(row["_field"], {}).get("unit", "NA"),
                                                  tagDict.get(row["_field"], {}).get("low3", "NA"),
                                                  tagDict.get(row["_field"], {}).get("low2", "NA"),
                                                  tagDict.get(row["_field"], {}).get("low", "NA"),
                                                  tagDict.get(row["_field"], {}).get("high", "NA"),
                                                  tagDict.get(row["_field"], {}).get("high2", "NA"),
                                                  tagDict.get(row["_field"], {}).get("high3", "NA"),
                                                  *irv_diagnose((row["Min"], row["Max"]), tagDict.get(row["_field"], None))]), axis=1)
    
    df.rename(columns = {"_field": "Field"}, inplace=True)
    
    # df = df[['_field', 
    #              'group',
    #              "description", 
    #              'unit', 
    #              'lll', 
    #              'll', 
    #              'l',
    #              'h',
    #              'hh',
    #              'hhh',
    #              'min',
    #              'max']]
    df = df.sort_values("Group")
    draw_table(df, height=700, title="MP Routing Monitoring")

def render_columns(devices, deviation_checks):
  print('render columns')
  col1, col2 = st.columns([1.5, 6])
  with col1:
    selected_device = get_device_by_name(devices, st.session_state["selected_device_name"])
    tags = selected_device["tags"] if selected_device is not None else []
    tags = filter(lambda tag: st.session_state["search_tags"].lower() in tag["tag_number"].lower(), tags)
    for tag in tags:
      st.checkbox(tag["tag_number"], True if tag["tag_number"] in st.session_state["tags"] else False, on_change=select_tag_update_calldb, args=(tag["tag_number"], ))

  with col2:
    st.write(st.session_state["tags"])
    # st.write(st.session_state)

    if st.session_state["raw_data"]:
      visualize_data_by_raw_data()


import streamlit.components.v1 as components

_component_func = components.declare_component("outstanding_tag_list", url="https://st.mmthub.freeddns.org/dist/")


def outstanding_tag_list(name, key=None, nMasks=[], oMasks=[], iMasks=[], fMasks=[], tags=[], tagDescriptions=[]):
  component_value = _component_func(name=name, key=key, default={}, nMasks=nMasks, oMasks=oMasks, iMasks=iMasks, fMasks=fMasks, tags=tags, tagDescriptions=tagDescriptions)
  return component_value


def render_outstanding_tags(container):
  print('render_outstanding_tags')
  if st.session_state["data"] is None:
    return
  df = st.session_state["data"].drop_duplicates(subset=['_measurement', '_field'], keep='last')[['_field', '_measurement', '_time']]
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
    nMasks = list(map(lambda x: pd.isnull(x), df['nan_check'].tolist())) if 'nan_check' in df.columns else [False] * _nTags
    oMasks = list(map(lambda x: pd.isnull(x), df['overange_check'].tolist())) if 'overange_check' in df.columns else [False] * _nTags
    iMasks = list(map(lambda x: pd.isnull(x), df['irv_check'].tolist())) if 'irv_check' in df.columns else [False] * _nTags
    fMasks = list(map(lambda x: pd.isnull(x), df['frozen_check'].tolist())) if 'frozen_check' in df.columns else [False] * _nTags

    tags = df["_field"].tolist()
    tagDict = load_tag_specs()

    selected_check_indices = outstanding_tag_list("Dummy", tags=tags, tagDescriptions=[tagDict.get(tag, {}).get('description', "") for tag in tags], nMasks=nMasks, oMasks=oMasks, iMasks=iMasks, fMasks=fMasks)
    try:
      st.session_state._selected_tag = None
      st.session_state._selected_checks = []
      if selected_check_indices['nIdx'] >= 0:
        st.session_state._selected_tag = df['_field'][selected_check_indices['nIdx']]
        st.session_state._selected_checks.append('nan_check')

      if selected_check_indices['oIdx'] >= 0:
        st.session_state._selected_tag = df['_field'][selected_check_indices['oIdx']]
        st.session_state._selected_checks.append('overange_check')

      if selected_check_indices['iIdx'] >= 0:
        st.session_state._selected_tag = df['_field'][selected_check_indices['iIdx']]
        st.session_state._selected_checks.append('irv_check')

      if selected_check_indices['fIdx'] >= 0:
        st.session_state._selected_tag = df['_field'][selected_check_indices['fIdx']]
        st.session_state._selected_checks.append('frozen_check')

    except:
      pass


def getRange(data):
  start = pd.to_datetime(data["_start"], errors='coerce').astype(np.int64).tolist()[0] // 10**9
  stop = pd.to_datetime(data["_stop"], errors='coerce').astype(np.int64).tolist()[0] // 10**9
  return (start, stop)


def render_inspection():
  df = st.session_state.data
  df = df[(df["_field"] == st.session_state._selected_tag)][['_time', '_field', "_value", '_measurement']]
  for check in st.session_state._selected_checks:
    df1 = df[df['_measurement'] == check]
    st.markdown(f"#### _{check}_")
    st.write(df1)

  time = f"{int(st.session_state['difference_time_range'])}s" if st.session_state["time_range"] == 0 else TIME_STRINGS[st.session_state["time_range"]]
  startStr, stopStr = getRange(st.session_state["data"])

  query = Query().from_bucket(BUCKET).range1(startStr, stopStr).filter_fields([st.session_state._selected_tag]).keep_columns("_time", "_value", "_field").aggregate_window(True).to_str()

  raw_data = query_api.query_data_frame(query, org=ORG)
  print(raw_data)
  raw_data["_time"] = raw_data["_time"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))
  raw_data["_start"] = raw_data["_start"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))
  raw_data["_stop"] = raw_data["_stop"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))

  if raw_data is not None:
    draw_chart_by_raw_data(raw_data, height=450, title=st.session_state._selected_tag, connected=True)
