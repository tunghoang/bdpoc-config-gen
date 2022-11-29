from configs.constants import DATE_NOW, TIME_STRINGS
from configs.module_loader import *
from utils.draw_chart import (draw_bar_chart_by_data_frame, draw_line_chart_by_data_frame)
from utils.influx_utils import (check_status, collector_status, query_check_all, query_check_data, query_irv_tags, query_raw_data, query_roc_tags)
from utils.tag_utils import load_tag_specs


def cal_different_time_range():
  # Calculate different time range
  return (st.session_state["end_time"] - st.session_state["start_time"]).total_seconds()


def select_tag_update_calldb(tag_number):
  if tag_number in st.session_state["tags"]:
    st.session_state["tags"].remove(tag_number)
  else:
    st.session_state["tags"].append(tag_number)
  #st.session_state["call_influx"] = True if len(st.session_state["tags"]) > 0 else False


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
  print('load_dataaaaaa')
  with st.spinner('Loading ...'):
    time = f"{int(st.session_state['difference_time_range'])}s" if st.session_state["time_range"] == 0 else TIME_STRINGS[st.session_state["time_range"]]
    if st.session_state["raw_data"]:
      st.session_state["data"] = query_raw_data(time, st.session_state['selected_device_name'], st.session_state["tags"], interpolated=st.session_state["interpolated"], missing_data=st.session_state["missing_data"])
    st.session_state['harvest_rate'] = collector_status()
    st.session_state['server_time'] = DATE_NOW().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["check_rate"] = check_status()


def load_all_check():
  print('load_all_check')
  with st.spinner('Loading ...'):
    time = f"{int(st.session_state['difference_time_range'])}s" if st.session_state["time_range"] == 0 else TIME_STRINGS[st.session_state["time_range"]]
    st.session_state['data'] = query_check_all(time)
    st.session_state['harvest_rate'] = collector_status()
    st.session_state['server_time'] = DATE_NOW().strftime("%Y-%m-%d %H:%M:%S")


def load_irv_tags():
  tagDict = load_tag_specs()
  with st.spinner("Loading irv tags ..."):
    time = f"{int(st.session_state['difference_time_range'])}s" if st.session_state["time_range"] == 0 else TIME_STRINGS[st.session_state["time_range"]]
    st.session_state["data"] = query_irv_tags(time)
    st.session_state['harvest_rate'] = collector_status()
    st.session_state['server_time'] = DATE_NOW().strftime("%Y-%m-%d %H:%M:%S")


def load_roc_tags():
  with st.spinner("Loading irv tags ..."):
    time = f"{int(st.session_state['difference_time_range'])}s" if st.session_state["time_range"] == 0 else TIME_STRINGS[st.session_state["time_range"]]
    st.session_state["data"] = query_roc_tags(time)
    st.session_state['harvest_rate'] = collector_status()
    st.session_state['server_time'] = DATE_NOW().strftime("%Y-%m-%d %H:%M:%S")


def visualize_data_by_raw_data():
  if st.session_state["data"] is not None and not st.session_state.data.empty:
    # st.write(st.session_state.data)
    draw_line_chart_by_data_frame(st.session_state["data"])
  else:
    print("No data-------")


def visualize_data_by_checks():
  draw_bar_chart_by_data_frame(st.session_state["data"], st.session_state["check_mode"])


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
