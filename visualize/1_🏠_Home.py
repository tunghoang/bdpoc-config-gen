from os import path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import yaml as yaml
from pandas import DataFrame

from css_call import local_css
from utilities import *
from influx_utils import query_data

# DEFAULT CHART STYLE
LINE_SHAPE = 'vh'
#LINE_SHAPE = 'linear'

TIME_STRINGS = {
    '10': '10s',
    '30': '30s',
    '60': '1m',
    '120': '2m',
    '300': '5m',
    '600': '10m',
    '1800': '30m'
}

# Initialize

st.set_page_config(page_title="Home", page_icon=":house:", layout="wide")

st.markdown(local_css(path.join(path.dirname(__file__), "assets", "style.css")), unsafe_allow_html=True)
if "tags" not in st.session_state:
    st.session_state["tags"] = []
if "selected_device_name" not in st.session_state:
    st.session_state["selected_device_name"] = ""
if "interpolated" not in st.session_state:
    st.session_state.interpolated = False
if "time_range" not in st.session_state:
    st.session_state.time_range = 10

# Load config file
control_logic_checks, deviation_checks, devices = load_tag_config()
with st.sidebar:
    for device in devices:
        st.button(f'{ "✔️" if device["label"] == st.session_state["selected_device_name"] else ""} {device["label"]}', key=device["label"], on_click=select_device, args=(device, ))

text = None
tCols = st.columns(4)
with tCols[0]:
    text = st.text_input("Search Tags", placeholder="Search for tags")
    text = text.lower()
with tCols[1]:
    st.session_state.interpolated = st.selectbox("Preprocessing", (True, False), format_func=lambda interpolated: "Interpolated" if interpolated else "Raw")
with tCols[2]:
    st.session_state.time_range = st.selectbox("Time Range", 
        (10, 30, 60, 120, 300, 600, 1800), format_func=lambda sec: TIME_STRINGS[str(sec)])
with tCols[3]:
    st.session_state.missing_data = st.selectbox("Fill missing data", ("NaN", "Last"))

col1, col2 = st.columns([1, 4])
with col1:
    selected_device = get_device_by_name(devices, st.session_state["selected_device_name"])
    tags = selected_device["tags"] if selected_device is not None else []
    tags = filter(lambda tag: text in tag["tag_number"].lower(), tags)
    for tag in tags:
        st.checkbox(tag["tag_number"], True if tag["tag_number"] in st.session_state["tags"] else False, on_change=select_tag, args=(tag["tag_number"], ))

with col2:
    #st.session_state["selected_device_name"]
    #st.session_state["tags"]

    # Load data from influxdb 
    with st.spinner('Loading ...'):
        data = query_data(TIME_STRINGS[str(st.session_state.time_range)], st.session_state['selected_device_name']
                , st.session_state["tags"], interpolated=st.session_state.interpolated, missing_data=st.session_state.missing_data)

    if "_time" in data:
        chart = px.line(data, x="_time", y="_value", labels = {
                "_time": "Time (s)",
                "_value": "Value",
                "_field": "Tag"
            }, color = '_field', 
            line_shape=LINE_SHAPE, 
            markers=True
        )
        st.plotly_chart(chart, use_container_width=True)

    st.empty()
    # device = get_data_by_device_name(random_data, devices, st.session_state["selected_device_name"])
    # if device is not None:
    #     tags = filter(lambda tag: tag["tag"] in st.session_state["tags"], device)
    #     for tag in tags:
    #         df = DataFrame.from_records(tag["data"])
    #         fig = px.line(data_frame=df, x="_time", y="_value", title=tag["tag"])
    #         st.plotly_chart(fig, use_container_width=True)
