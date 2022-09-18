from logging import PlaceHolder
from os import path
import time

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import yaml as yaml
from pandas import DataFrame
import asyncio
import streamlit_nested_layout

from css_call import local_css
from utilities import *
from influx_utils import query_data

def init():
    st.set_page_config(page_title="Home", page_icon=":house:", layout="wide")

    st.markdown(local_css(path.join(path.dirname(__file__), "assets", "style.css")), unsafe_allow_html=True)
    if "tags" not in st.session_state:
        st.session_state["tags"] = []
    if "selected_device_name" not in st.session_state:
        st.session_state["selected_device_name"] = ""
    if "data" not in st.session_state:
        st.session_state["data"] = []
    if "call_influx" not in st.session_state:
        st.session_state["call_influx"] = False

async def main():
    print("rerendered")
    # Initialize
    init()

    # Load config file
    control_logic_checks, deviation_checks, devices = load_tag_config()
    with st.sidebar:
        for device in devices:
            st.button(f'{ "✔️" if device["label"] == st.session_state["selected_device_name"] else ""} {device["label"]}', key=device["label"], on_click=select_device, args=(device, ))

    placeholder = st.empty()
    if st.session_state["call_influx"]:
        with st.spinner("Loading..."):
            placeholder.empty()
            st.session_state["data"] = await query_data("15m", st.session_state['selected_device_name'], st.session_state["tags"])
            st.session_state["call_influx"] = False
    with placeholder.container():
        col1, col2 = placeholder.columns([1, 4])
        with col1:
            col1.text_input("", placeholder="Search for tags", key="text_search")
            selected_device = get_device_by_name(devices, st.session_state["selected_device_name"])
            tags = selected_device["tags"] if selected_device is not None else []
            tags = filter(lambda tag: tag["tag_number"].lower().find(st.session_state["text_search"].lower()) > -1, tags)
            for tag in tags:
                col1.checkbox(tag["tag_number"], True if tag["tag_number"] in st.session_state["tags"] else False, on_change=select_tag, args=(tag["tag_number"], ))

        with col2:
            container = st.empty()
            _, sub_col = container.columns([4, 1])
            st.session_state["selected_device_name"]
            st.session_state["tags"]
            sub_col.button("Filter", on_click=call_db)

            # Load data from influxdb
            data = st.session_state["data"]
            if "_time" in data:
                chart = px.line(data, x="_time", y="_value", labels={"_time": "Time (s)", "_value": "Value", "_field": "Tag"}, color='_field')
                col2.plotly_chart(chart, use_container_width=True)

if __name__ == '__main__':
    asyncio.run(main())
