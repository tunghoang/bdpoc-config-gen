from operator import itemgetter
import yaml

def cfg_load_tag_config():
    with open("tags.yaml", "r") as yaml_file:
        control_logic_checks, deviation_checks, devices = itemgetter("control_logic_checks", "deviation_checks", "devices")(yaml.safe_load(yaml_file))
        devices.sort(key=lambda device: device["label"])
        return (control_logic_checks, deviation_checks, devices)
