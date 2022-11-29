import streamlit.components.v1 as components
from configs.constants import (CUSTOM_DATAFRAME_PREVIEW, CUSTOM_DATAFRAME_RELEASE, OUTSTANDING_TAG_RELEASE)
from custom_components.st_dataframe_component import \
    st_custom_dataframe as st_custom_dataframe_lib
from custom_components.tag_list import \
    outstanding_tag_list as outstanding_tag_list_lib


def custom_component(com_name, url="", component_lib=None, release=False, **kwargs):
  if not release:
    _custom_component = components.declare_component(com_name, url=url)
    return _custom_component(**kwargs)
  return component_lib(**kwargs)


def st_custom_dataframe(data, header = "", key = 0, withSearch=False, withComment=False, withDownload=False):
  return custom_component(com_name="st_custom_dataframe", url=CUSTOM_DATAFRAME_PREVIEW, component_lib=st_custom_dataframe_lib, release=CUSTOM_DATAFRAME_RELEASE, data=data, header=header, key=key, withSearch=withSearch, withComment=withComment, withDownload=withDownload)


def outstanding_tag_list(name, key=None, nMasks=[], oMasks=[], iMasks=[], fMasks=[], tags=[], tagDescriptions=[]):
  return custom_component(com_name="out_standing_tag", component_lib=outstanding_tag_list_lib, release=OUTSTANDING_TAG_RELEASE, name=name, key=key, nMasks=nMasks, oMasks=oMasks, iMasks=iMasks, fMasks=fMasks, tags=tags, tagDescriptions=tagDescriptions)
