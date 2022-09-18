from operator import itemgetter

import numpy as np
import pandas as pd
import streamlit as st
import yaml

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

def get_data_by_device_name(data, devices, device_name):
	device = get_device_by_name(devices, device_name)
	if device is not None:
		return data[device['label']]

@st.cache
def load_tag_config():
	with open("tags.yaml", "r") as yaml_file:
		control_logic_checks, deviation_checks, devices = itemgetter("control_logic_checks", "deviation_checks", "devices")(yaml.safe_load(yaml_file))
		devices.sort(key=lambda device: device["label"])
		return (control_logic_checks, deviation_checks, devices)

@st.cache
def random(devices):
	random_data = {}
	for device in devices:
		tags = []
		for tag in device["tags"]:
			_tag = []
			for i in range(100):
				_tag.append({"_value": np.random.randint(100), "_time": pd.Timestamp.now() + pd.Timedelta(seconds=i)})
			tags.append({"tag": tag["tag_number"], "data": _tag})
		random_data[device['label']] = tags
	return random_data
