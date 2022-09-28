from module_loader import *

from css_call import *
from views import *

def init():
    # Initialize
    st.set_page_config(page_title="Home", page_icon=":house:", layout="wide")
    st.markdown(local_css(path.join(path.dirname(__file__), "assets", "style.css")), unsafe_allow_html=True)
    # Init session
    init_session("tags", [])
    init_session("search_tags", "")
    init_session("selected_device_name", "")
    init_session("interpolated", False)
    init_session("time_range", 10)
    init_session("start_time", DATE_NOW() - dt.timedelta(days=1))
    init_session("end_time", DATE_NOW())
    init_session("difference_time_range", cal_different_time_range())
    init_session("chart_mode", "all")
    init_session("table_mode", "thin")
    init_session("pivot_state", False)
    init_session("call_influx", False)
    init_session("data", pd.DataFrame())

def main():
    init()
    # Load config file
    control_logic_checks, deviation_checks, devices = load_tag_config()
    with st.sidebar:
        load_sidebar(devices)

    placeholder = st.empty()
    if (st.session_state["call_influx"]):
        placeholder = st.empty()
        load_data()
        st.session_state["call_influx"] = False
    with placeholder.container():
        load_configuration()
        load_columns(devices)

if __name__ == "__main__":
    main()
