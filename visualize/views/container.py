import json, copy, traceback
from datetime import timedelta
from itertools import islice

import dateutil.parser as parser
import numpy as np
import pandas as pd
import pytz
import streamlit as st
from configs.constants import (BUCKET, INFINITIES, LABELS, ORG, START_DERIVATIVE_VALUE, STOP_DERIVATIVE_VALUE, TIME_STRINGS)

from configs.custom_components import outstanding_tag_list, st_custom_dataframe
from custom_components.st_custom_selector import st_custom_selector

from configs.influx_client import query_api
from configs.query import Query
from utils.draw_chart import (draw_chart_by_check_data, draw_chart_by_raw_data, draw_table, draw_barchart, draw_wet_seal_chart)
from utils.influx_utils import query_irv_transient_tags
from utils.session import sess, update_session
from utils.tag_utils import load_tag_specs
from utils.view_utils import (get_device_by_name, select_tag_update_calldb, visualize_data_by_raw_data)

from configs.logger import check_logger

from influx import Influx


def render_overview():
  filename = tagSpecFile(sess("current_machine"))
  check_logger.info(filename)
  tag_dict = load_tag_specs(filename)
  df = sess("data")
  if df is None:
    return
  df = df[df._field.isin(tag_dict.keys())]
  draw_chart_by_check_data(df, title=f"{sess('current_machine').upper()} Alert Overview")

def render_wet_seals():
  df = sess("data")
  if df is None:
    return
  df = df[df._field.isin(['LP_Seal', "IP_Seal"])]
  check_logger.info(df._field)
  draw_wet_seal_chart(df, title="Wet Seals Alarms/PreAlarms")
  st.markdown("""----
### LP WetGas Rules: 
- Alarm if: discharge_count_in_1day >= 5 and drop_level_in_1day > 0.5%
- PreAlarm if: 
  1. discharge_count_in_1day >= 5 and drop_level_in_1day < 0.5%
  2. or discharge_count_in_1day > 2 and drop_level_in_1day > 0.4%
- Normal: otherwise
----
### IP WetGas Rules: 
- Alarm if: discharge_count_in_13day >= 4 and drop_level_in_1day >= 0.3% 
- PreAlarm if : 
  1. discharge_count_in_13day >= 4 and drop_level_in_1day < 0.3% 
  2. discharge_count_in_13day >= 2 and drop_level_in_1day >= 0.15%
- Normal if: otherwise
"""
  )

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
  shutdown_limits = [tagSpec["low3"], tagSpec["high3"]]
  alarm_limits = [tagSpec["low2"], tagSpec["high2"]]
  prealarm_limits = [tagSpec["low"], tagSpec["high"]]

  flags = [0, 0]
  output = ""

  for i in range(0, 2):
    if inside(min_max[i], INFINITIES[i], shutdown_limits[i]):
      if shutdown_limits[i] != alarm_limits[i]:
        flags[i] = 3
        comment = f"{LABELS[i]} - ALARM;"
      elif alarm_limits[i] != prealarm_limits[i]:
        flags[i] = 2
        comment = f"{LABELS[i]} - PREALARM;"
      else:
        flags[i] = 1
        comment = f"{LABELS[i]} - {'INCREASING' if i > 0 else 'DECREASING'};"
      output = output + comment
    elif inside(min_max[i], shutdown_limits[i], alarm_limits[i]):
      # results["alarms"][i] = True
      flags[i] = 2
      output = output + f"{LABELS[i]} - PREALARM;"
    elif inside(min_max[i], alarm_limits[i], prealarm_limits[i]):
      # results["prealarms"][i] = True
      flags[i] = 1
      output = output + f"{LABELS[i]} - {'INCREASING' if i > 0 else 'DECREASING'};"
    elif inside(min_max[i], prealarm_limits[0], prealarm_limits[1]):
      # results["normals"][i] = True
      flags[i] = 0
      output = output + f"{LABELS[i]} - NORMAL;"
  return max(flags[0], flags[1]), output

def tagSpecFile(device = "mp"):
  return 'assets/files/tag-specs.yaml' if device == "mp" else 'assets/files/lip-tag-specs.yaml'

def irvTableData(df, device="mp"):
  filename = tagSpecFile(device)
  check_logger.info(filename)
  tagDict = load_tag_specs(filename)
  df = df.groupby("_field", as_index=False)._value.agg({"Min": lambda x: min(list(x)), "Max": lambda x: max(list(x))})

  df[["Group", "Description", "Unit", "LLL", "LL", "L", "H", "HH", "HHH", "Flag", "Evaluation"]] = df.apply(
    lambda row: pd.Series([
      tagDict.get(row["_field"], {}).get("device", "NA"),
      tagDict.get(row["_field"], {}).get("description", "NA"),
      tagDict.get(row["_field"], {}).get("unit", "NA"),
      tagDict.get(row["_field"], {}).get("low3", "NA"),
      tagDict.get(row["_field"], {}).get("low2", "NA"),
      tagDict.get(row["_field"], {}).get("low", "NA"),
      tagDict.get(row["_field"], {}).get("high", "NA"),
      tagDict.get(row["_field"], {}).get("high2", "NA"),
      tagDict.get(row["_field"], {}).get("high3", "NA"), *irv_diagnose((row["Min"], row["Max"]), tagDict.get(row["_field"], None), row["_field"])
    ]), axis=1
  )

  df.rename(columns={"_field": "Field"}, inplace=True)

  df = df.sort_values("Group")
  records = df.to_dict("records")
  return records


def __irvTable(df, header="", device="mp", withSearch=False, withComment=False, withDownload=False, key=0):
  records = irvTableData(df, device)
  st_custom_dataframe(data=records, header=header, withSearch=withSearch, withComment=withComment, withDownload=withDownload, key=key)

def render_irv_report(device = "mp"):
  if sess("data") is not None:
    df = sess("data")[["_field", "_value"]]
    __irvTable(df, header=f"{device.upper()} Routing Monitoring", device=device, withSearch=True, withComment=True, withDownload=True)
  
def render_transient_report(device = 'mp'):
  check_logger.info("render_transient_report")
  st.subheader(f"{device.upper()} Transient Report")
  if sess("data") is not None:
    if sess("data").empty:
      return st.markdown("<h3 class='no-mp-data'>No stop and start period</h3>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(['Report', 'Analyse'])
    all_df = pd.DataFrame()
    with tab1:
      for idx, row in sess("data").iterrows():
        offset = 0 if row._value < 0 else 2
        length = 5 if row._value < 0 else 10
        check_logger.info(f"{length}")
        startTime = row._time.to_pydatetime() + timedelta(minutes=offset)
        stopTime = startTime + timedelta(minutes=length)
        check_logger.info("++++++++++000++++++++++++")
        check_logger.info(f"{startTime}, {stopTime}")
        alert_type = "STOP" if row["_value"] < 0 else "START"

        df = query_irv_transient_tags(startTime, stopTime, alert_type)
        all_df = pd.concat([all_df, copy.deepcopy(df)])
        header = {
            "alert_type": "STOP" if row["_value"] < 0 else "START",
            "start": str(startTime),
            "end": str(stopTime),
        }
        __irvTable(df, device=device, header=header, key=idx)
    
    with tab2:
      all_df = all_df[["startTime", "_value", "_field", "alert_type"]]
      all_df.sort_values(["startTime", "_field", "_value"], inplace=True)
      all_df.reset_index(inplace=True, drop=True)
      all_df['minmax'] = all_df.index.map(lambda i: 'min' if i % 2 == 0 else 'max')
      labels = {
        "startTime": "Time",
        "_value": "Value",
        "minmax": "Legend",
        "_field": "Tag",
        "alert_type": "Type"
      }
      _dummy, filtered_df = st_custom_selector(key=1, data=all_df)
      check_logger.info(f'TYPE: {type(filtered_df)}')
      if filtered_df is None:
        filtered_df = pd.DataFrame()
      check_logger.info(f'TYPE: {type(filtered_df)}')
      all_df.to_csv('/tmp/all_df.csv')
      if filtered_df is not None and not filtered_df.empty:
        filtered_df.columns = filtered_df.columns.get_level_values(0)

        filtered_df.to_csv('/tmp/filtered_df.csv')
        #col_num=1 if device == 'mp' else 3,
        col_num = 1
        #height = 13 * 150 if device == 'mp' else 14 * 150
        check_logger.info(filtered_df['_field'].unique())
        height = len(filtered_df._field.unique()) * 150
        draw_barchart(
          filtered_df, 
          x = 'startTime', 
          y = '_value', 
          color='minmax', 
          facet="_field",
          labels=labels,
          hover_data={"_value": ":.3f"},
          height = height,
          col_num=col_num,
          domain=[
            parser.isoparse(f"{sess('start_date')}T{sess('start_time')}+07:00"),
            parser.isoparse(f"{sess('end_date')}T{sess('end_time')}+07:00")
          ]
        )
      check_logger.info(_dummy);

def render_columns(devices, deviation_checks):
  check_logger.info('render columns')
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
  device = sess("current_machine")
  check_logger.info(f"render_outstanding_tags, {device}")
  if sess("data") is None:
    return
  filename = tagSpecFile(device)
  tagDict = load_tag_specs(filename)
  df = sess("data")
  df = df[df._field.isin(tagDict.keys())]
  df = df.drop_duplicates(subset=['_measurement', '_field'], keep='last')[['_field', '_measurement', '_time']]
  df = df.pivot(index='_field', columns='_measurement')
  df = df['_time'].reset_index()
  df.columns.name = None

  check_logger.info("111111111111111111111111111")
  check_logger.info(df._field)

  _nTags = df['_field'].count()

  with container.container():
    st.markdown('''<div
      class="streamlit-expanderHeader st-ae st-bw st-ag st-ah st-ai st-aj st-bx st-by st-bz st-c0 st-c1 st-c2 st-c3 st-ar st-as st-c4 st-c5 st-b3 st-c6 st-c7 st-c8 st-b4 st-c9 st-ca st-cb st-cc st-cd"
      style="background:white;">⚙ 💗 🔥 OUTSTANDING TAGS</div>
    ''',
                unsafe_allow_html=True)
    nMasks = list(
      map(lambda x: pd.isnull(x), df['nan_check'].tolist())
    ) if 'nan_check' in df.columns else [True] * _nTags
    oMasks = list(map(lambda x: pd.isnull(x), df['overange_check'].tolist())) if 'overange_check' in df.columns else [True] * _nTags
    iMasks = list(map(lambda x: pd.isnull(x), df['irv_check'].tolist())) if 'irv_check' in df.columns else [True] * _nTags
    fMasks = list(map(lambda x: pd.isnull(x), df['frozen_check'].tolist())) if 'frozen_check' in df.columns else [True] * _nTags
    rMasks = list(map(lambda x: pd.isnull(x), df['roc_check'].tolist())) if 'roc_check' in df.columns else [True] * _nTags
    
    #check_logger.info(df['frozen_check'])

    tags = df["_field"].tolist()
    #tagDict = load_tag_specs(tagSpecFile(device))

    selected_check_indices = outstanding_tag_list("Dummy", tags=tags, tagDescriptions=[tagDict.get(tag, {}).get('description', "") for tag in tags], nMasks=nMasks, oMasks=oMasks, iMasks=iMasks, fMasks=fMasks, rMasks=rMasks)
    try:
      check_logger.info(f"{selected_check_indices}")
      update_session("_selected_tag", None)
      update_session("_selected_checks", [])
      if selected_check_indices.get('nIdx', -1) >= 0:
        update_session("_selected_tag", df['_field'][selected_check_indices['nIdx']])
        sess("_selected_checks").append('nan_check')

      if selected_check_indices.get('oIdx', -1) >= 0:
        update_session("_selected_tag", df['_field'][selected_check_indices['oIdx']])
        sess("_selected_checks").append('overange_check')

      if selected_check_indices.get('iIdx', -1) >= 0:
        update_session("_selected_tag", df['_field'][selected_check_indices['iIdx']])
        sess("_selected_checks").append('irv_check')

      if selected_check_indices.get('fIdx', -1) >= 0:
        update_session("_selected_tag", df['_field'][selected_check_indices['fIdx']])
        sess("_selected_checks").append('frozen_check')
        
      if selected_check_indices.get('rIdx', -1) >= 0:
        update_session("_selected_tag", df['_field'][selected_check_indices['rIdx']])
        sess("_selected_checks").append('roc_check')
      check_logger.info(sess("_selected_checks"))
    except:
      traceback.print_exc()
      pass


def getRange(data):
  start = pd.to_datetime(data["_start"], errors='coerce').astype(np.int64).tolist()[0] // 10**9
  stop = pd.to_datetime(data["_stop"], errors='coerce').astype(np.int64).tolist()[0] // 10**9
  return (start, stop)


def render_inspection():
  df = sess("data")
  df = df[(df["_field"] == sess("_selected_tag"))][['_time', '_field', "_value", '_measurement', "type"]]
  st.write(df)
  for check in sess("_selected_checks"):
    df1 = df[df['_measurement'] == check]
    st.markdown(f"#### _{check}_")
    st.write(df1)
  raw_data = Influx().addField(
    sess("_selected_tag")
  ).setStart(
    parser.isoparse(f'{sess("start_date")}T{sess("start_time")}+07:00')
  ).setStop(
    parser.isoparse(f'{sess("end_date")}T{sess("end_time")}+07:00')
  ).asDataFrame()
  #time_range_settings = TIME_STRINGS[sess('view_mode')]
  #time = f"{int(sess('difference_time_range'))}s" if sess("time_range") == 0 else time_range_settings[sess('time_range')]
  #startStr, stopStr = getRange(sess("data"))

  #query = Query().from_bucket(BUCKET).range1(startStr, stopStr).filter_fields(sess("_selected_tag")).keep_columns("_time", "_value", "_field").aggregate_window(True).to_str()

  #raw_data = query_api.query_data_frame(query, org=ORG)
  #raw_data["_time"] = raw_data["_time"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))
  #raw_data["_start"] = raw_data["_start"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))
  #raw_data["_stop"] = raw_data["_stop"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))

  if (raw_data is not None) and (not raw_data.empty):
    draw_chart_by_raw_data(raw_data, height=450, title=sess("_selected_tag"), connected=True)
