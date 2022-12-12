import traceback

from configs.constants import DATE_NOW, TIME_STRINGS, VIEW_MODES
from configs.module_loader import *
from utils.css_utils import local_css
from utils.influx_utils import check_status, collector_status
from utils.session import init_session
from utils.tag_utils import load_tag_config
from utils.view_utils import (cal_different_time_range, load_all_check, load_data, load_irv_tags, load_roc_tags, visualize_data_by_raw_data)
from views.container import (render_inspection, render_irv_report, render_outstanding_tags, render_overview, render_roc_report)
from views.sidebar import render_sidebar


def init():
  # Initialize
  st.set_page_config(page_title="Home", page_icon=":house:", layout="wide")
  st.markdown(local_css(path.join(path.dirname(__file__), "assets", "style.css")), unsafe_allow_html=True)
  # Init session
  init_session("tags", [])
  init_session("missing_data", "NaN")
  init_session("view_mode", 0)
  init_session("search_tags", "")
  init_session("selected_device_name", "")
  init_session("interpolated", False)
  init_session("time_range", 300)
  init_session("start_time", DATE_NOW() - dt.timedelta(days=1))
  init_session("end_time", DATE_NOW())
  init_session("difference_time_range", cal_different_time_range())
  init_session("chart_mode", "all")
  init_session("call_influx", False)
  #init_session("data", pd.DataFrame())
  init_session("data", None)
  init_session("harvest_rate", collector_status())
  init_session("check_rate", check_status())
  init_session("server_time", DATE_NOW().strftime("%Y-%m-%d %H:%M:%S"))
  #init_session("tabs", ["Overview"])
  init_session("_selected_tag", None)
  init_session("_selected_checks", {})
  init_session("nFlags", None)
  init_session("oFlags", None)
  init_session("iFlags", None)
  init_session("fFlags", None)


def apply():
  st.session_state.data = None
  st.session_state._selected_tag = None
  st.session_state._selected_checks.clear()
  st.session_state["call_influx"] = True


def reset_session():
  st.session_state["tags"] = []
  st.session_state._selected_tag = None
  st.session_state._selected_checks = {}
  st.session_state["data"] = None


def setting_controls():
  st.button("Fetch & View", on_click=apply, type="primary")
  st.selectbox("View Mode", (0, 1, 2, 3), format_func=lambda viewModeIdx: VIEW_MODES[viewModeIdx], key="view_mode", on_change=reset_session)

  with st.expander("⚙ SETTINGS", True):
    if st.session_state["time_range"] == 0:
      start_date, end_date = st.columns([1, 1])
      with start_date:
        st.date_input("Start Date", value=st.session_state["start_time"], key="start_date", on_change=cal_different_time_range)
      with end_date:
        st.date_input("End Date", value=st.session_state["end_time"], key="end_date", on_change=cal_different_time_range)
    time_range_settings = TIME_STRINGS[st.session_state['view_mode']]
    print(time_range_settings)
    st.selectbox("Time Range", options=time_range_settings.keys(), format_func=lambda sec: time_range_settings[sec], key="time_range", on_change=reset_session)

    if st.session_state["view_mode"] == 1:
      st.selectbox("Preprocessing", (True, False), index=0 if st.session_state["interpolated"] else 1, format_func=lambda interpolated: "Interpolated" if interpolated else "Raw")

      st.selectbox("Fill missing data", ("NaN", "Last"), key="missing_data")

      st.selectbox("Chart Style", ("all", "merge"), key="chart_mode")

def main():
  init()
  # Load config file
  control_logic_checks, deviation_checks, devices = load_tag_config()
  with st.sidebar:
    setting_controls()
    if st.session_state["view_mode"] == 1:
      render_sidebar(devices)

  try:
    if st.session_state["call_influx"]:
      print("query data")
      st.session_state["call_influx"] = False
      if st.session_state["view_mode"] < 2:
        if len(st.session_state["tags"]) > 0:
          load_data()
        else:
          load_all_check()
      elif st.session_state["view_mode"] == 2:
        load_irv_tags()
      elif st.session_state["view_mode"] == 3:
        load_roc_tags()

    with st.container():
      st.markdown(f"""<div id='app-title'>Instrument Health Monitoring</div><div id='info'>
        <div><b>Server time </b>: {st.session_state['server_time']}</div>
        <div><b>Harvest rate</b>: {st.session_state['harvest_rate']} tags/s</div>
        <div><b>Check rate</b>: {st.session_state['check_rate']} check/min</div>
      </div>""",
                  unsafe_allow_html=True)

      #render_configurations()
      if st.session_state["view_mode"] == 1:
        visualize_data_by_raw_data()
      elif st.session_state["view_mode"] == 0:
        render_overview()
      elif st.session_state["view_mode"] == 2:
        render_irv_report()
      elif st.session_state["view_mode"] == 3:
        render_roc_report()
      st.empty()

    if st.session_state["view_mode"] == 0:
      render_outstanding_tags(st.sidebar)

    if st.session_state["data"] is not None and st.session_state["_selected_tag"] is not None:
      st.subheader(f"Alert inspection for {st.session_state._selected_tag}")
      render_inspection()
  except Exception:
    traceback.print_exc()
    st.error("Noooo data found. Extend 'Time Range' to retrieve more data", icon="❗")
    st.session_state["data"] = None


if __name__ == "__main__":
  main()
