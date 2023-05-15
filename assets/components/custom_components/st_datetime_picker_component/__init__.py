import os
import streamlit.components.v1 as components

parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "frontend/build")
_component_func = components.declare_component("st_datetime_picker_component", path=build_dir)


def st_datetime_picker(key=None):
	name = _component_func.name
	component_value = _component_func(key=key)
	return name, component_value
