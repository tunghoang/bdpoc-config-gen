import streamlit as st

def local_css(file_name):
	with open(file_name) as css:
		st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)