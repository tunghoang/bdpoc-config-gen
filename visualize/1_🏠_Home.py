from os import path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import yaml as yaml
from pandas import DataFrame

from css_call import local_css
from utilities import *

# Initialize

st.set_page_config(page_title="Home", page_icon=":house:", layout="wide")

local_css(path.join(path.dirname(__file__), "assets", "style.css"))
if "tags" not in st.session_state:
	st.session_state["tags"] = []
if "selected_device_name" not in st.session_state:
	st.session_state["selected_device_name"] = ""

control_logic_checks, deviation_checks, devices = load_data()
random_data = random(devices)

with st.sidebar:
	for device in devices:
		st.button(f'{ "✔️" if device["label"] == st.session_state["selected_device_name"] else ""} {device["label"]}', key=device["label"], on_click=select_device, args=(device, ))

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
	device = get_data_by_device_name(random_data, devices, st.session_state["selected_device_name"])
	if device is not None:
		tags = filter(lambda tag: tag["tag"] in st.session_state["tags"], device)
		for tag in tags:
			df = DataFrame.from_records(tag["data"])
			fig = px.line(data_frame=df, x="_time", y="_value", title=tag["tag"])
			st.plotly_chart(fig, use_container_width=True)
