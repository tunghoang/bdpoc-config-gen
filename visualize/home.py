import sys
import views as v
import utilities as u
from constants import *
from css_call import local_css
from module_loader import *
# from checks import check_schedule

def init():
    # Initialize
    st.set_page_config(page_title="Home", page_icon=":house:", layout="wide")
    st.markdown(local_css(path.join(path.dirname(__file__), "assets", "style.css")), unsafe_allow_html=True)
    # Init session
    v.init_session("tags", [])
    v.init_session("search_tags", "")
    v.init_session("selected_device_name", "")
    v.init_session("interpolated", False)
    v.init_session("time_range", 10)
    v.init_session("start_time", DATE_NOW() - dt.timedelta(days=1))
    v.init_session("end_time", DATE_NOW())
    v.init_session("difference_time_range", u.cal_different_time_range())
    v.init_session("chart_mode", "all")
    v.init_session("table_mode", "thin")
    v.init_session("pivot_state", False)
    v.init_session("call_influx", False)
    v.init_session("data", pd.DataFrame())

def main():
    init()
    # Load config file
    control_logic_checks, deviation_checks, devices = v.load_tag_config()
    with st.sidebar:
        v.load_sidebar(devices)

    placeholder = st.empty()
    if (st.session_state["call_influx"]):
        placeholder = st.empty()
        v.load_data()
        st.session_state["call_influx"] = False
    with placeholder.container():
        v.load_configuration()
        v.load_columns(devices)

if __name__ == "__main__":
    main()
