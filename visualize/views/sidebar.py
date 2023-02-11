import streamlit as st
from utils.session import sess
from utils.view_utils import get_device_by_name, select_tag_update_calldb


def render_sidebar(devices):
  with st.expander("Devices", expanded=True):
    st.text_input("Search Tags", placeholder="Search for tags", key="search_tags")
    for device in devices:
      with st.expander(device["label"]):
        selected_device = get_device_by_name(devices, device["label"])
        tags = selected_device["tags"] if selected_device is not None else []
        tags = filter(lambda tag: sess("search_tags").lower() in tag["tag_number"].lower(), tags)
        for tag in tags:
          st.checkbox(tag["tag_number"], True if tag["tag_number"] in sess("tags") else False, on_change=select_tag_update_calldb, args=(tag["tag_number"], ))
