from utils.tag_utils import load_tag_config


class TagConfig:
  def __init__(self, yaml_file_path):
    self.yaml_file_path = yaml_file_path
    self.control_logic_checks, self.deviation_checks, self.devices = load_tag_config(self.yaml_file_path)