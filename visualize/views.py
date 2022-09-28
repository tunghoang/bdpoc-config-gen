from module_loader import *

from constants import *
from utilities import *
from checks import *
from influx_utils import *

def init_session(name, value):
    if name not in st.session_state:
        st.session_state[name] = value

def draw_line_chart_by_data_frame(data, pivot=False):
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

def load_configuration():
    with st.expander("Configurations", True):
        if st.session_state["time_range"] == 0:
            start_date, end_date = st.columns([1, 1])
            with start_date:
                st.date_input("Start Date", value=st.session_state["start_time"], key="start_date", on_change=cal_different_time_range)
            with end_date:
                st.date_input("End Date", value=st.session_state["end_time"], key="end_date", on_change=cal_different_time_range)
        tCols = st.columns([1.5, 1, 1, 1, 1, 1])
        with tCols[0]:
            st.text_input("Search Tags", placeholder="Search for tags", key="search_tags")
        with tCols[1]:
            st.selectbox("Preprocessing", (True, False), index=0 if st.session_state["interpolated"] else 1, format_func=lambda interpolated: "Interpolated" if interpolated else "Raw", on_change=update_interpolated_calldb)
        with tCols[2]:
            st.selectbox("Time Range", (10, 30, 60, 120, 300, 600, 1800, 0), format_func=lambda sec: TIME_STRINGS[str(sec)], key="time_range", on_change=update_calldb)
        with tCols[3]:
            st.selectbox("Fill missing data", ("NaN", "Last"), key="missing_data", on_change=update_calldb)
        with tCols[4]:
            st.selectbox("Chart Mode", ("all", "merge"), key="chart_mode", on_change=update_calldb)
        with tCols[5]:
            st.selectbox("Table Mode", ("thin", "fat"), key="table_mode", on_change=update_pivot_calldb)

def load_columns(devices):
    col1, col2 = st.columns([1.5, 6])
    with col1:
        selected_device = get_device_by_name(devices, st.session_state["selected_device_name"])
        tags = selected_device["tags"] if selected_device is not None else []
        tags = filter(lambda tag: st.session_state["search_tags"].lower() in tag["tag_number"].lower(), tags)
        for tag in tags:
            st.checkbox(tag["tag_number"], True if tag["tag_number"] in st.session_state["tags"] else False, on_change=select_tag_update_calldb, args=(tag["tag_number"], ))

    with col2:
        st.write(st.session_state["tags"])
        # st.write(st.session_state)

        if not st.session_state["data"].empty:
            # Load data from influxdb
            if (st.session_state["nan"]):
                nan = nan_check_multi(st.session_state["data"], st.session_state["tags"], st.session_state["pivot_state"])
                st.write(nan)
            if (st.session_state["overange"]):
                overange = overange_check(st.session_state["data"], st.session_state["tags"], st.session_state["pivot_state"])
                st.write(overange)
            if (st.session_state["irv"]):
                irv = irv_check(st.session_state["data"], st.session_state["tags"], st.session_state["pivot_state"])
                st.write(irv)
            draw_line_chart_by_data_frame(st.session_state["data"], st.session_state["pivot_state"])

def load_sidebar(devices):
    for check in CHECKS_LIST.keys():
        st.button(check, key=CHECKS_LIST[check])
    st.markdown("---")
    for device in devices:
        st.button(f'{ "✔️" if device["label"] == st.session_state["selected_device_name"] else ""} {device["label"]}', on_click=select_device, args=(device, ))

@st.cache
def load_tag_config():
    with open("tags.yaml", "r") as yaml_file:
        control_logic_checks, deviation_checks, devices = itemgetter("control_logic_checks", "deviation_checks", "devices")(yaml.safe_load(yaml_file))
        devices.sort(key=lambda device: device["label"])
        return (control_logic_checks, deviation_checks, devices)
