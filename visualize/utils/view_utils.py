from configs.constants import TIME_STRINGS
from configs.module_loader import *
from utils.influx_utils import *

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
        time = f"{int(st.session_state['difference_time_range'])}s" if st.session_state["time_range"] == 0 else TIME_STRINGS[str(st.session_state["time_range"])]
        st.session_state["data"] = query_data(time, st.session_state['selected_device_name'], st.session_state["tags"], interpolated=st.session_state["interpolated"], missing_data=st.session_state["missing_data"], table_mode=st.session_state["table_mode"])

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
