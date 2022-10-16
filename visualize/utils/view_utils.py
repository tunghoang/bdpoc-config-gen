from configs.checks import (deviation_check, frozen_check, irv_check, nan_check, overange_check, roc_check)
from configs.constants import PIVOT, TIME_STRINGS
from configs.module_loader import *

from utils.draw_chart import (draw_bar_chart_by_data_frame, draw_line_chart_by_data_frame)
from utils.influx_utils import query_check_data, query_raw_data


def cal_different_time_range():
  # Calculate different time range
  return (st.session_state["end_time"] - st.session_state["start_time"]).total_seconds()


def select_tag_update_calldb(tag_number):
  if tag_number in st.session_state["tags"]:
    st.session_state["tags"].remove(tag_number)
  else:
    st.session_state["tags"].append(tag_number)
  st.session_state["call_influx"] = True if len(st.session_state["tags"]) > 0 else False


def get_device_by_name(devices, device_name):
  for device in devices:
    if device['label'] == device_name:
      return device


def select_device(device):
  st.session_state["selected_device_name"] = device['label']
  st.session_state["tags"][:] = []


def get_data_by_device_name(data, devices, device_name):
  device = get_device_by_name(devices, device_name)
  if device is not None:
    return data[device['label']]


def load_data():
  with st.spinner('Loading ...'):
    time = f"{int(st.session_state['difference_time_range'])}s" if st.session_state["time_range"] == 0 else TIME_STRINGS[st.session_state["time_range"]]
    if st.session_state["raw_data"]:
      st.session_state["data"] = query_raw_data(time, st.session_state['selected_device_name'], st.session_state["tags"], interpolated=st.session_state["interpolated"], missing_data=st.session_state["missing_data"])
      return
    st.session_state['data'] = query_check_data(time, st.session_state['selected_device_name'], st.session_state["tags"], st.session_state["check_mode"])


def visualize_data_by_raw_data(devices, deviation_checks):
  # Load data from influxdb
  if (st.session_state["check_mode"] == "nan_check" or st.session_state["check_mode"] == "all"):
    nan = nan_check(st.session_state["data"], st.session_state["tags"])
    draw_bar_chart_by_data_frame(nan, "nan_check")
  if (st.session_state["check_mode"] == "overange_check" or st.session_state["check_mode"] == "all"):
    overange = overange_check(st.session_state["data"], devices, st.session_state["tags"])
    draw_bar_chart_by_data_frame(overange, "overange_check")
  if (st.session_state["check_mode"] == "irv_check" or st.session_state["check_mode"] == "all"):
    irv = irv_check(st.session_state["data"], devices, st.session_state["tags"])
    draw_bar_chart_by_data_frame(irv, "irv_check")
  if (st.session_state["check_mode"] == "deviation_check" or st.session_state["check_mode"] == "all"):
    deviation = deviation_check(st.session_state["data"], deviation_checks, devices)
    draw_bar_chart_by_data_frame(deviation, "deviation_check")
  if (st.session_state["check_mode"] == "roc_check" or st.session_state["check_mode"] == "all"):
    roc = roc_check(st.session_state["data"], devices)
    draw_bar_chart_by_data_frame(roc, "roc_check")
  if (st.session_state["check_mode"] == "frozen_check" or st.session_state["check_mode"] == "all"):
    frozen = frozen_check(st.session_state["data"], devices)
    draw_bar_chart_by_data_frame(frozen, "frozen_check")
  draw_line_chart_by_data_frame(st.session_state["data"])


def visualize_data_by_checks():
  for data in st.session_state["data"]:
    # st.write(data)
    draw_bar_chart_by_data_frame(data)


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
