import streamlit as st
from configs.constants import CHECKS_LIST, TIME_STRINGS
from utils.session import (update_calldb_session,
                           update_interpolated_calldb_session,
                           update_pivot_calldb_session)
from utils.view_utils import (cal_different_time_range, get_device_by_name,
                              select_tag_update_calldb,
                              visualize_data_by_checks,
                              visualize_data_by_raw_data)


def render_configurations():
  with st.expander("Configurations", True):
    if st.session_state["time_range"] == 0:
      start_date, end_date = st.columns([1, 1])
      with start_date:
        st.date_input("Start Date", value=st.session_state["start_time"], key="start_date", on_change=cal_different_time_range)
      with end_date:
        st.date_input("End Date", value=st.session_state["end_time"], key="end_date", on_change=cal_different_time_range)
    tCols = st.columns([1.5, 1, 1, 1, 1, 1, 2])
    with tCols[0]:
      st.text_input("Search Tags", placeholder="Search for tags", key="search_tags")
    with tCols[1]:
      if st.session_state["raw_data"]:
        st.selectbox("Preprocessing", (True, False), index=0 if st.session_state["interpolated"] else 1, format_func=lambda interpolated: "Interpolated" if interpolated else "Raw", on_change=update_interpolated_calldb_session)
      else:
        st.selectbox("Preprocessing", (True, False), index=0 if st.session_state["interpolated"] else 1, format_func=lambda interpolated: "Interpolated" if interpolated else "Raw", on_change=update_interpolated_calldb_session, disabled=True)
    with tCols[2]:
      st.selectbox("Time Range", options=TIME_STRINGS.keys(), format_func=lambda sec: TIME_STRINGS[sec], key="time_range", on_change=update_calldb_session)
    with tCols[3]:
      if st.session_state["raw_data"]:
        st.selectbox("Fill missing data", ("NaN", "Last"), key="missing_data", on_change=update_calldb_session)
      else:
        st.selectbox("Fill missing data", ("NaN", "Last"), key="missing_data", on_change=update_calldb_session, disabled=True)
    with tCols[4]:
      st.selectbox("Chart Mode", ("all", "merge"), key="chart_mode", on_change=update_calldb_session)
    with tCols[5]:
      st.selectbox("Raw data", (True, False), key="raw_data")
    with tCols[6]:
      st.selectbox("Check mode", CHECKS_LIST.keys(), format_func=lambda check_mode: CHECKS_LIST[check_mode], key="check_mode", on_change=update_calldb_session)


def render_columns(devices):
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
    else:
      visualize_data_by_checks()
