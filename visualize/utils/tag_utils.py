from operator import itemgetter

import streamlit as st
import yaml


@st.cache
def load_tag_config(filename="assets/files/tags.yaml"):
  with open(filename, "r") as yaml_file:
    control_logic_checks, deviation_checks, devices = itemgetter("control_logic_checks", "deviation_checks", "devices")(yaml.safe_load(yaml_file))
    devices.sort(key=lambda device: device["label"])
    return control_logic_checks, deviation_checks, devices


@st.cache
def load_tag_specs(filename="assets/files/tag-specs.yaml"):
  with open(filename, "r") as yaml_file:
    tagDict = yaml.safe_load(yaml_file)
    return tagDict