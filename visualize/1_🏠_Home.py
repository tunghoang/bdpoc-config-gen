from os import path
import plotly.express as px
import streamlit as st
import pandas as pd
from pandas import DataFrame
import numpy as np
import yaml as yaml
from operator import itemgetter

# Utilities
def select_tag(tag_number):
	if tag_number in st.session_state.tags:
		st.session_state.tags.remove(tag_number)
	else:
		st.session_state.tags.append(tag_number)

def get_device_by_name(devices, device_name):
	for device in devices:
		if device['label'] == device_name:
			return device

def select_device(device):
	st.session_state["selected_device_name"] = device['label']
	st.session_state.tags[:] = []

@st.cache
def load_data():
	with open("tags.yaml", "r") as yaml_file:
		control_logic_checks, deviation_checks, devices = itemgetter("control_logic_checks", "deviation_checks", "devices")(yaml.safe_load(yaml_file))
		devices.sort(key=lambda device: device["label"])
		return (control_logic_checks, deviation_checks, devices)

# Initialize
# from css_call import local_css

st.set_page_config(page_title="Home", page_icon=":house:", layout="wide")

# local_css(path.join(path.dirname(__file__), "assets", "style.css"))
if "tags" not in st.session_state:
	st.session_state.tags = []
if "selected_device_name" not in st.session_state:
	st.session_state.selected_device_name = ""

control_logic_checks, deviation_checks, devices = load_data()

with st.sidebar:
	for device in devices:
		st.button(f'{ "✔️" if device["label"] == st.session_state["selected_device_name"] else ""} {device["label"]}', on_click=select_device, args=(device, ))

col1, col2 = st.columns([1, 4])
with col1:
	text = st.text_input("", placeholder="Search for tags")

	selected_device = get_device_by_name(devices, st.session_state["selected_device_name"])
	tags = selected_device["tags"] if selected_device is not None else []
	tags = filter(lambda tag: tag["tag_number"].lower().startswith(text.lower()), tags)
	for tag in tags:
		st.checkbox(tag["tag_number"], True if tag["tag_number"] in st.session_state.tags else False, on_change=select_tag, args=(tag["tag_number"], ))

with col2:
	st.session_state.selected_device_name
	st.session_state.tags
	x = np.arange(0, 2 * np.pi, 0.01)
	y = np.sin(x)
	source = DataFrame({"horizontal": x, "vertical": y})
	fig = px.line(data_frame=source, x="horizontal", y="vertical")
	st.plotly_chart(fig, use_container_width=True)