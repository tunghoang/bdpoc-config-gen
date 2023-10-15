from configs.constants import DATE_NOW, TIME_STRINGS
from configs.module_loader import *
from utils.draw_chart import (draw_bar_chart_by_data_frame, draw_line_chart_by_data_frame)
from utils.influx_utils import (check_status, collector_status, query_check_all, query_check_seals, query_check_vibration, query_irv_tags, query_transient_periods, query_raw_data, get_raw_data, query_roc_tags, get_rul_tags)
from utils.session import apply, sess, update_session
from utils.tag_utils import load_tag_specs
from dateutil import parser as dparser
from configs.logger import check_logger

def cal_different_time_range():
  # Calculate different time range
  total_seconds = (dt.datetime.combine(sess("end_date"), sess("end_time")) - dt.datetime.combine(sess("start_date"), sess("start_time"))).total_seconds()
  update_session("difference_time_range", total_seconds)
  return total_seconds


def select_tag_update_calldb(tag_number):
  if tag_number in sess("tags"):
    sess("tags").remove(tag_number)
  else:
    sess("tags").append(tag_number)
  #sess("call_influx"] = True if len(st.session_state["tags")) > 0 else False


def get_device_by_name(devices, device_name):
  for device in devices:
    if device['label'] == device_name:
      return device


def select_device(device):
  update_session("selected_device_name", device['label'])
  update_session("tags", [])


def get_data_by_device_name(data, devices, device_name):
  device = get_device_by_name(devices, device_name)
  if device is not None:
    return data[device['label']]


def load_data():
  check_logger.info('load_dataaaaaa')
  with st.spinner('Loading ...'):
    apply(
      data=get_raw_data(
        sess("start_date"), sess("start_time"),
        sess("end_date"), sess("end_time"), 
        sess("tags"),
        sess("sampling_rate")
      ), 
      harvest_rate=collector_status(), 
      server_time=DATE_NOW().strftime("%Y-%m-%d %H:%M:%S"), 
      check_rate=check_status()
    )
def load_seal_check():
  check_logger.info("load_seal_check")
  with st.spinner('Loading ...'):
    start = dparser.isoparse(f"{sess('start_date')}T{sess('start_time')}+07:00")
    end = dparser.isoparse(f"{sess('end_date')}T{sess('end_time')}+07:00")
    apply(
      data=query_check_seals(start, end),
      harvest_rate=collector_status(), 
      server_time=DATE_NOW().strftime("%Y-%m-%d %H:%M:%S"), 
      check_rate=check_status()
    )

def load_vibration_check():
  check_logger.info("load_vibration_check")
  with st.spinner("Loading ..."):
    start = dparser.isoparse(f"{sess('start_date')}T{sess('start_time')}+07:00")
    end = dparser.isoparse(f"{sess('end_date')}T{sess('end_time')}+07:00")
    apply(
      data=query_check_vibration(start, end),
      harvest_rate=collector_status(), 
      server_time=DATE_NOW().strftime("%Y-%m-%d %H:%M:%S"), 
      check_rate=check_status()
    )
def load_all_check():
  check_logger.info('load_all_check')
  #time_range_settings = TIME_STRINGS[sess('view_mode')]
  with st.spinner('Loading ...'):
    #time = f"{int(sess('difference_time_range'))}s" if sess("time_range") == 0 else time_range_settings[sess('time_range')]
    start = dparser.isoparse(f"{sess('start_date')}T{sess('start_time')}+07:00")
    end = dparser.isoparse(f"{sess('end_date')}T{sess('end_time')}+07:00")
    apply(
      data=query_check_all(start, end), 
      harvest_rate=collector_status(), 
      server_time=DATE_NOW().strftime("%Y-%m-%d %H:%M:%S")
    )


def load_irv_tags():
  # tagDict = load_tag_specs()
  #time_range_settings = TIME_STRINGS[sess('view_mode')]
  with st.spinner("Loading irv tags ..."):
    start = dparser.isoparse(f"{sess('start_date')}T{sess('start_time')}+07:00")
    end = dparser.isoparse(f"{sess('end_date')}T{sess('end_time')}+07:00")
    #time = f"{int(sess('difference_time_range'))}s" if sess("time_range") == 0 else time_range_settings[sess('time_range')]
    apply(data=query_irv_tags(start, end), harvest_rate=collector_status(), server_time=DATE_NOW().strftime("%Y-%m-%d %H:%M:%S"))


def load_transient_periods(device="mp"):
  time_range_settings = TIME_STRINGS[sess('view_mode')]
  with st.spinner("Loading transient periods ..."):
    start = dparser.isoparse(f"{sess('start_date')}T{sess('start_time')}+07:00")
    end = dparser.isoparse(f"{sess('end_date')}T{sess('end_time')}+07:00")
    #time = f"{int(sess('difference_time_range'))}s" if sess("time_range") == 0 else time_range_settings[sess('time_range')]
    apply(
      data=query_transient_periods(start, end, device), 
      harvest_rate=collector_status(), 
      server_time=DATE_NOW().strftime("%Y-%m-%d %H:%M:%S")
    )


def load_roc_tags():
  time_range_settings = TIME_STRINGS[sess('view_mode')]
  with st.spinner("Loading irv tags ..."):
    time = f"{int(sess('difference_time_range'))}s" if sess("time_range") == 0 else time_range_settings[sess('time_range')]
    apply(data=query_roc_tags(time), harvest_rate=collector_status(), server_time=DATE_NOW().strftime("%Y-%m-%d %H:%M:%S"))

def load_rul_data():
  with st.spinner("Loading RUL data ..."):
    start = dparser.isoparse(f"{sess('start_date')}T{sess('start_time')}+07:00")
    end = dparser.isoparse(f"{sess('end_date')}T{sess('end_time')}+07:00")
    apply(data=get_rul_tags(start, end), harvest_rate=collector_status(), server_time=DATE_NOW().strftime("%Y-%m-%d %H:%M:%S"))

def visualize_data_by_raw_data():
  if sess("data") is not None and not sess("data").empty:
    # st.write(sess("data)")
    draw_line_chart_by_data_frame(sess("data"))
  else:
    check_logger.info("No data-------")


def visualize_data_by_checks():
  draw_bar_chart_by_data_frame(sess("data"), sess("check_mode"))


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
