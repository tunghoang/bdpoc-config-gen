import datetime

import streamlit as st
from configs.logger import check_logger
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
    },
    #type='primary'
  )
  st.selectbox(
    "Machine",
    MACHINES,
    key="current_machine",
    format_func=lambda machine: machine.upper(),
    on_change=apply, 
    kwargs={
      "data": None, 
      "_selected_tag": None, 
      "_selected_checks": [], 
      "time_range": 0,
      "tags": []
    }
      
  )
  st.selectbox(
    "View Mode", 
    list(range(len(VIEW_MODES[sess("current_machine")]))),
    #(OVERVIEW, RAW_DATA, ROUTINE_REPORT, TRANSIENT_REPORT), 
    format_func=lambda viewModeIdx: VIEW_MODES[sess("current_machine")][viewModeIdx], 
    key="view_mode", 
    on_change=apply, 
    kwargs={
      "data": None, 
      "_selected_tag": None, 
      "_selected_checks": [], 
      "time_range": 0,
      "tags": []
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
    if sess("view_mode") == RAW_DATA:
      st.selectbox("Rate", ('60s', '30s', '10s', '5s', '1s'), key="sampling_rate")


class Sidebar:
  def render(self, app, machine, devices):
    check_logger.info(f"render sidebar -- {machine}")
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
              check_logger.info(tag["tag_number"]);
              st.checkbox(tag["tag_number"], True if tag["tag_number"] in sess("tags") else False, on_change=select_tag_update_calldb, args=(tag["tag_number"], ))
