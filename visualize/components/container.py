from utils.session import sess
from configs.constants import OVERVIEW, RAW_DATA, ROUTINE_REPORT, TRANSIENT_REPORT
from utils.view_utils import visualize_data_by_raw_data
from views.container import (render_inspection, render_irv_report, render_mp_transient_report, render_overview, render_outstanding_tags)
import streamlit as st
#from views.container import (render_inspection, render_irv_report,
#                             render_mp_transient_report,
#                             render_outstanding_tags, render_overview)

class Container:
  def render(self):
    #render_configurations()
    if sess("view_mode") == RAW_DATA:
      #sess("data")
      visualize_data_by_raw_data()
    elif sess("view_mode") == OVERVIEW:
      render_overview()
      render_outstanding_tags(st.sidebar)
      print("sess_data", sess("data"))
      print("sess_selected_tag", sess("_selected_tag"))
      if sess("data") is not None and sess("_selected_tag") is not None:
        st.subheader(f"Alert inspection for {sess('_selected_tag')}")
        render_inspection()
    elif sess("view_mode") == ROUTINE_REPORT:
      render_irv_report()
    elif sess("view_mode") == TRANSIENT_REPORT:
      #render_roc_report()
      render_mp_transient_report()