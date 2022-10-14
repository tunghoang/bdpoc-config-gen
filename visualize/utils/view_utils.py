from configs.checks import irv_check, nan_check, overange_check
from configs.constants import TIME_STRINGS
from configs.module_loader import *

from utils.draw_line_chart import draw_line_chart_by_data_frame
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
      st.session_state["data"] = query_raw_data(time, st.session_state['selected_device_name'], st.session_state["tags"], interpolated=st.session_state["interpolated"], missing_data=st.session_state["missing_data"], table_mode=st.session_state["table_mode"])
      return
    st.session_state['data'] = query_check_data(time, st.session_state['selected_device_name'], st.session_state["tags"], st.session_state["check_mode"])


def visualize_data_by_raw_data():
  # Load data from influxdb
  if (st.session_state["check_mode"] == "nan_check"):
    nan = nan_check(st.session_state["data"], st.session_state["tags"], st.session_state["pivot_state"])
    st.write(nan)
  if (st.session_state["check_mode"] == "overange_check"):
    overange = overange_check(st.session_state["data"], st.session_state["tags"], st.session_state["pivot_state"])
    st.write(overange)
  if (st.session_state["check_mode"] == "irv_check"):
    irv = irv_check(st.session_state["data"], st.session_state["tags"], st.session_state["pivot_state"])
    st.write(irv)
  # if (st.session_state["check_mode"] == "deviation_check"):
  #   deviation = deviation_check(st.session_state["data"], st.session_state["tags"], st.session_state["pivot_state"])
  #   st.write(deviation)
  # if (st.session_state["check_mode"] == "roc_check"):
  #   roc = roc_check(st.session_state["data"], st.session_state["tags"], st.session_state["pivot_state"])
  #   st.write(roc)
  # draw_line_chart_by_data_frame(st.session_state["data"], st.session_state["pivot_state"])


def visualize_data_by_checks():
  if type(st.session_state["data"]) == list:
    for data in st.session_state["data"]:
      st.write(data)
    return
  st.write(st.session_state["data"])


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
