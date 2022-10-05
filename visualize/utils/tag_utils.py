from operator import itemgetter
import streamlit as st
import yaml

@st.cache
def load_tag_config():
    with open("tags.yaml", "r") as yaml_file:
        control_logic_checks, deviation_checks, devices = itemgetter("control_logic_checks", "deviation_checks", "devices")(yaml.safe_load(yaml_file))
        devices.sort(key=lambda device: device["label"])
        return control_logic_checks, deviation_checks, devices
