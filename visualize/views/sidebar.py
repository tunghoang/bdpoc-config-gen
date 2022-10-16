import streamlit as st
from utils.view_utils import select_device


def render_sidebar(devices):
  st.text_input("Search Tags", placeholder="Search for tags", key="search_tags")
  st.subheader("Devices")
  for device in devices:
    st.button(f'{ "✔️" if device["label"] == st.session_state["selected_device_name"] else ""} {device["label"]}', on_click=select_device, args=(device, ))
