import streamlit as st


def init_session(name, value):
    if name not in st.session_state:
        st.session_state[name] = value

def update_call_db_session():
    st.session_state["call_influx"] = True

def update_interpolated_calldb_session():
    st.session_state["interpolated"] = not st.session_state["interpolated"]
    st.session_state["call_influx"] = True

def update_calldb_session():
    st.session_state["call_influx"] = True

def update_pivot_calldb_session():
    st.session_state["call_influx"] = True
