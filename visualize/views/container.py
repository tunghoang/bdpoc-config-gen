import streamlit as st
from configs.constants import TIME_STRINGS
from utils.view_utils import cal_different_time_range, get_device_by_name, select_tag_update_calldb
from utils.session import update_interpolated_calldb_session, update_calldb_session, update_pivot_calldb_session
from utils.draw_line_chart import draw_line_chart_by_data_frame
from configs.checks import nan_check, overange_check, irv_check

def render_configurations():
    with st.expander("Configurations", True):
        if st.session_state["time_range"] == 0:
            start_date, end_date = st.columns([1, 1])
            with start_date:
                st.date_input("Start Date", value=st.session_state["start_time"], key="start_date", on_change=cal_different_time_range)
            with end_date:
                st.date_input("End Date", value=st.session_state["end_time"], key="end_date", on_change=cal_different_time_range)
        tCols = st.columns([1.5, 1, 1, 1, 1, 1])
        with tCols[0]:
            st.text_input("Search Tags", placeholder="Search for tags", key="search_tags")
        with tCols[1]:
            st.selectbox("Preprocessing", (True, False), index=0 if st.session_state["interpolated"] else 1, format_func=lambda interpolated: "Interpolated" if interpolated else "Raw", on_change=update_interpolated_calldb_session)
        with tCols[2]:
            st.selectbox("Time Range", (10, 30, 60, 120, 300, 600, 1800, 0), format_func=lambda sec: TIME_STRINGS[str(sec)], key="time_range", on_change=update_calldb_session)
        with tCols[3]:
            st.selectbox("Fill missing data", ("NaN", "Last"), key="missing_data", on_change=update_calldb_session)
        with tCols[4]:
            st.selectbox("Chart Mode", ("all", "merge"), key="chart_mode", on_change=update_calldb_session)
        with tCols[5]:
            st.selectbox("Table Mode", ("thin", "fat"), key="table_mode", on_change=update_pivot_calldb_session)

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

        if not st.session_state["data"].empty:
            # Load data from influxdb
            if (st.session_state["nan"]):
                nan = nan_check(st.session_state["data"], st.session_state["tags"], st.session_state["pivot_state"])
                st.write(nan)
            if (st.session_state["overange"]):
                overange = overange_check(st.session_state["data"], st.session_state["tags"], st.session_state["pivot_state"])
                st.write(overange)
            if (st.session_state["irv"]):
                irv = irv_check(st.session_state["data"], st.session_state["tags"], st.session_state["pivot_state"])
                st.write(irv)
            draw_line_chart_by_data_frame(st.session_state["data"], st.session_state["pivot_state"])