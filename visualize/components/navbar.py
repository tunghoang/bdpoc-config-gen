import streamlit as st
from utils.session import sess


class Navbar:
  def render(self):
    st.markdown(f"""<div id='app-title'>Instrument Health Monitoring</div><div id='info'>
            <div><b>Server time </b>: {sess('server_time')}</div>
            <div><b>Harvest rate</b>: {sess('harvest_rate')} tags/s</div>
            <div><b>Check rate</b>: {sess('check_rate')} check/min</div>
          </div>""", unsafe_allow_html=True)