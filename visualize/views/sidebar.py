import streamlit as st
from utils.view_utils import select_device


def render_sidebar(devices):
  for device in devices:
    st.button(f'{ "✔️" if device["label"] == st.session_state["selected_device_name"] else ""} {device["label"]}', on_click=select_device, args=(device, ))
