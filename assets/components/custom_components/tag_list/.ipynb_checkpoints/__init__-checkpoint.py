import os

import streamlit.components.v1 as components

parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "frontend/dist")

_outstanding_tag_list = components.declare_component("outstanding_tag_list", path=build_dir)


def outstanding_tag_list(name, key=None, nMasks=[], oMasks=[], iMasks=[], fMasks=[], rMasks=[] tags=[], tagDescriptions=[]):
  component_value = _outstanding_tag_list(name=name, key=key, default={}, nMasks=nMasks, oMasks=oMasks, iMasks=iMasks, fMasks=fMasks, rMasks=rMasks, tags=tags, tagDescriptions=tagDescriptions)
  return component_value