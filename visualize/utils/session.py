import streamlit as st


def init_session(app, name, value):
  app.sessions[name] = value
  if name not in st.session_state:
    st.session_state[name] = value


def update_session(name, new_value):
  st.session_state[name] = new_value


def sess(name):
  return st.session_state[name]


def apply(**sessions):
  for name, value in sessions.items():
    update_session(name, value)


def reset_session(app, *session_names):
  for name in session_names:
    if name in st.session_state:
      update_session(name, app.sessions[name])
  # print(app.sessions)