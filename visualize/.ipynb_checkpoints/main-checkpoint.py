from configs.constants import DATE_NOW
from configs.module_loader import *
from utils.css_utils import local_css
from utils.session import init_session
from utils.tag_utils import load_tag_config
from utils.view_utils import cal_different_time_range, load_data
from views.container import render_columns, render_configurations
from views.sidebar import render_sidebar

# from checks import check_schedule


def init():
  # Initialize
  st.set_page_config(page_title="Home", page_icon=":house:", layout="wide")
  st.markdown(local_css(path.join(path.dirname(__file__), "assets", "style.css")), unsafe_allow_html=True)
  # Init session
  init_session("tags", [])
  init_session("missing_data", "NaN")
  init_session("raw_data", True)
  init_session("search_tags", "")
  init_session("selected_device_name", "")
  init_session("interpolated", False)
  init_session("time_range", 10)
  init_session("start_time", DATE_NOW() - dt.timedelta(days=1))
  init_session("end_time", DATE_NOW())
  init_session("difference_time_range", cal_different_time_range())
  init_session("chart_mode", "all")
  init_session("call_influx", False)
  init_session("data", pd.DataFrame())


def main():
  init()
  # Load config file
  control_logic_checks, deviation_checks, devices = load_tag_config()
  with st.sidebar:
    render_sidebar(devices)

  placeholder = st.empty()
  if (st.session_state["call_influx"]):
    placeholder = st.empty()
    load_data()
    st.session_state["call_influx"] = False
  with placeholder.container():
    render_configurations()
    render_columns(devices)


if __name__ == "__main__":
  main()
