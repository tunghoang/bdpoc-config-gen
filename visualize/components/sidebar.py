import datetime

import streamlit as st
from configs.constants import MACHINES, TIME_STRINGS, VIEW_MODES, OVERVIEW, RAW_DATA, ROUTINE_REPORT, TRANSIENT_REPORT
from utils.session import apply, reset_session, sess
from utils.view_utils import (cal_different_time_range, get_device_by_name,
                              select_tag_update_calldb)
from views.container import render_outstanding_tags

def setting_controls(app):
  st.button(
    "Fetch & View", 
    on_click=apply, 
    kwargs={
      "data": None, 
      "_selected_tag": None, 
      "_selected_checks": [], 
      "call_influx": True
    }
  )
  st.selectbox(
      "Machine",
      MACHINES,
      key="current_machine",
      format_func=lambda machine: machine.upper(),
  )
  st.selectbox(
    "View Mode", 
    (OVERVIEW, RAW_DATA, ROUTINE_REPORT, TRANSIENT_REPORT), 
    format_func=lambda viewModeIdx: VIEW_MODES[sess("current_machine")][viewModeIdx], 
    key="view_mode", 
    on_change=apply, 
    kwargs={
      "data": None, 
      "_selected_tag": None, 
      "_selected_checks": [], 
      "time_range": 0
    }
  )

  with st.expander("⚙ SETTINGS", True):
    if sess("time_range") == 0:
      st.markdown("-------------")
      col1, col2 = st.columns([3, 3])
      with col1:
        st.date_input("Start Date", value=sess("start_date"), key="start_date", on_change=cal_different_time_range)
        st.date_input("End Date", value=sess("end_date"), key="end_date", on_change=cal_different_time_range)
      with col2:
        st.time_input("Start Time", value=sess("start_time"), key="start_time", on_change=cal_different_time_range)
        st.time_input("End Time", value=sess("end_time"), key="end_time", on_change=cal_different_time_range)
      #time_range_settings = TIME_STRINGS[sess('view_mode')]
      #st.selectbox("Time Range", options=time_range_settings.keys(), format_func=lambda sec: time_range_settings[sec], key="time_range", on_change=reset_session, args=(app, "data", "_selected_tag", "_selected_checks", "tags"))

    if sess("view_mode") == RAW_DATA:
      #st.selectbox("Preprocessing", (True, False), index=0 if sess("interpolated") else 1, format_func=lambda interpolated: "Interpolated" if interpolated else "Raw")
      #st.selectbox("Fill missing data", ("NaN", "Last"), key="missing_data")
      #st.selectbox("Chart Style", ("all", "merge"), key="chart_mode")
      st.selectbox("Rate", ('60s', '30s', '10s', '5s', '1s'), key="sampling_rate")


class Sidebar:
  def render(self, app, machine, devices):
    setting_controls(app)
    if sess("view_mode") == RAW_DATA:
      with st.expander("Devices", expanded=True):
        st.text_input("Search Tags", placeholder="Search for tags", key="search_tags")
        for device in devices:
          with st.expander(device["label"]):
            selected_device = get_device_by_name(devices, device["label"])
            tags = selected_device["tags"] if selected_device is not None else []
            tags = filter(lambda tag: sess("search_tags").lower() in tag["tag_number"].lower(), tags)
            for tag in tags:
              st.checkbox(tag["tag_number"], True if tag["tag_number"] in sess("tags") else False, on_change=select_tag_update_calldb, args=(tag["tag_number"], ))
