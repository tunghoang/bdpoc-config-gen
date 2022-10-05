from typing import List
import streamlit as st
import datetime as dt
import pandas as pd
import plotly.express as px
from configs.constants import DATE_NOW, LINE_SHAPE

def draw_line_chart_by_data_frame(data: pd.DataFrame, pivot: bool = False) -> List[st._DeltaGenerator]:
    range = st.session_state["difference_time_range"] if st.session_state["time_range"] == 0 else int(st.session_state["time_range"])
    time_range_in_datetime = [DATE_NOW() - dt.timedelta(seconds=range), DATE_NOW()]
    if pivot:
        # Convert pivot to normal dataframe
        data = pd.melt(data, id_vars=["_time"], value_vars=st.session_state["tags"], value_name="_value", var_name="_field")
    if st.session_state["chart_mode"] == "merge":
        chart = px.line(data, x="_time", y="_value", labels={"_time": "Time (s)", "_value": "Value", "_field": "Tag"}, color='_field', line_shape=LINE_SHAPE, markers=True, range_x=time_range_in_datetime)
        return st.plotly_chart(chart, use_container_width=True)
    charts = []
    for tag in st.session_state["tags"]:
        chart = px.line(data[data["_field"] == tag], x="_time", y="_value", labels={"_time": "Time (s)", "_value": tag, "_field": "Tag"}, line_shape=LINE_SHAPE, markers=True, range_x=time_range_in_datetime)
        charts.append(st.plotly_chart(chart, use_container_width=True))
    return charts