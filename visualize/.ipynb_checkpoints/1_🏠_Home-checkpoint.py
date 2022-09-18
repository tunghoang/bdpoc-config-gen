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

# Initialize

st.set_page_config(page_title="Home", page_icon=":house:", layout="wide")

st.markdown(local_css(path.join(path.dirname(__file__), "assets", "style.css")), unsafe_allow_html=True)
if "tags" not in st.session_state:
	st.session_state["tags"] = []
if "selected_device_name" not in st.session_state:
	st.session_state["selected_device_name"] = ""

# Load config file
control_logic_checks, deviation_checks, devices = load_tag_config()
# Load data from influxdb 
st.session_state['loading'] = True
data = query_data("1m", st.session_state['selected_device_name'], st.session_state["tags"])
st.session_state['loading'] = False

with st.sidebar:
	for device in devices:
		st.button(f'{ "✔️" if device["label"] == st.session_state["selected_device_name"] else ""} {device["label"]}', key=device["label"], on_click=select_device, args=(device, ), disabled=st.session_state['loading'])

col1, col2 = st.columns([1, 4])
with col1:
	text = st.text_input("", placeholder="Search for tags")
	selected_device = get_device_by_name(devices, st.session_state["selected_device_name"])
	tags = selected_device["tags"] if selected_device is not None else []
	tags = filter(lambda tag: tag["tag_number"].lower().startswith(text.lower()), tags)
	for tag in tags:
		st.checkbox(tag["tag_number"], True if tag["tag_number"] in st.session_state["tags"] else False, on_change=select_tag, args=(tag["tag_number"], ))

with col2:
	st.session_state["selected_device_name"]
	st.session_state["tags"]
	if "_time" in data:
		chart = px.line(data, x="_time", y="_value")
		st.plotly_chart(chart, use_container_width=True, labels = {
            "_time": "Time (s)", 
            "_value": ','.join(st.session_state['tags'])
        })

	st.empty()
	# device = get_data_by_device_name(random_data, devices, st.session_state["selected_device_name"])
	# if device is not None:
	# 	tags = filter(lambda tag: tag["tag"] in st.session_state["tags"], device)
	# 	for tag in tags:
	# 		df = DataFrame.from_records(tag["data"])
	# 		fig = px.line(data_frame=df, x="_time", y="_value", title=tag["tag"])
	# 		st.plotly_chart(fig, use_container_width=True)
