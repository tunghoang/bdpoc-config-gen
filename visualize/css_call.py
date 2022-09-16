import streamlit as st

@st.cache
def local_css(file_name):
	with open(file_name) as css:
		return f'<style>{css.read()}</style>'