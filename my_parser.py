import getopt
import sys
from operator import itemgetter

import yaml

from config_gen import csv_to_array_full_objects

# HEADER NAME CONSTANTS ###
__OVERANGE_CHECK_NAME = ["overange_check", "overange_check"]
__IRV_CHECK_NAME = ["instrument_range_validation", "irv_check"]
__NAN_CHECK_NAME = ["nan_check", "nan_check"]
__ROC_CHECK_NAME = ["rate_of_change_check", "roc_check"]
__FROZEN_CHECK_NAME = ["frozen_check_(5_min_configurable)", "frozen_check"]
__TRAVELLING_CHECK_NAME = ["travelling_check", "travelling_check"]
__DEVIATION_CHECK_NAME = ["cross_ref.__(deviation_check)__number", "deviation_check"]
__CONTROL_LOGIC_CHECK_NAME = ["control_logic_check__number", "control_logic_check"]
__DESCRIPTION = ["measuring_point", "description"]
__MP_STARTUP = ["mp_startup", "mp_startup"]

_YAML_FILE = "assets/files/tags.yaml"

_TAG_LIST_FILE = "assets/files/tag_list.csv"
# PARAMETER NAME CONSTANTS ###
__OVERANGE_CHECK_PARAM_NAMES = ["low", "high"]
__IRV_CHECK_PARAM_NAMES = ["low3", "low2", "low", "high", "high2", "high3"]


def usage():
  print("Usage:")
  print("python main.py [option]")
  print("\t-i, --input\t\tInput file")
  print("\t-o, --output\t\tOutput file")
  print("\t-h, --help\t\tPrint this help")


def init():
  file_input = _TAG_LIST_FILE
  output_file_name = _YAML_FILE
  try:
    options, _ = getopt.getopt(sys.argv[1:], "i:o:h", ["input=", "output=", "help"])
  except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(2)
  for opt, arg in options:
    if opt in ("-i", "--input"):
      file_input = arg
    elif opt in ("-o", "--output"):
      output_file_name = arg
    elif opt in ("-h", "--help"):
      usage()
      sys.exit()
    else:
      assert False, "unhandled option"
  data = csv_to_array_full_objects(file_input)
  return {"data": data, "output_file_name": output_file_name}


def add_device_tags(devices, name):
  if name not in devices:
    devices[name] = {}
  return devices[name]


def process_description(tagObject, tagInfor):
  if __DESCRIPTION[0] in tagObject:
    tagObject[__DESCRIPTION[1]] = tagInfor[__DESCRIPTION[0]]


def process_nan_check(tagObject, tagInfor):
  if __NAN_CHECK_NAME[0] in tagObject and tagInfor[__NAN_CHECK_NAME[0]] == "Y":
    tagObject[__NAN_CHECK_NAME[1]] = True


def process_overange_check(tagObject, tagInfor):
  if __OVERANGE_CHECK_NAME[0] in tagObject:
    params = tagInfor[__OVERANGE_CHECK_NAME[0]].split(",")
    if len(params) != 2:
      return
    paramsHash = {}
    for idx, param in enumerate(params):
      if param == "_":
        paramsHash[__OVERANGE_CHECK_PARAM_NAMES[idx]] = None
      else:
        paramsHash[__OVERANGE_CHECK_PARAM_NAMES[idx]] = float(param)
    tagObject[__OVERANGE_CHECK_NAME[1]] = paramsHash


def process_irv_check(tagObject, tagInfor):
  if __IRV_CHECK_NAME[0] in tagObject:
    params = tagInfor[__IRV_CHECK_NAME[0]].split(",")
    if len(params) != 6:
      return
    paramsHash = {}
    for idx, param in enumerate(params):
      if param == "_":
        paramsHash[__IRV_CHECK_PARAM_NAMES[idx]] = None
      else:
        paramsHash[__IRV_CHECK_PARAM_NAMES[idx]] = float(param)
    tagObject[__IRV_CHECK_NAME[1]] = paramsHash


def process_roc_check(tagObject, tagInfor):
  if __ROC_CHECK_NAME[0] in tagObject:
    if tagInfor[__ROC_CHECK_NAME[0]] == "":
      return
    tagObject[__ROC_CHECK_NAME[1]] = tagInfor[__ROC_CHECK_NAME[0]]


def process_frozen_check(tagObject, tagInfor):
  if __FROZEN_CHECK_NAME[0] in tagObject and tagInfor[__FROZEN_CHECK_NAME[0]] == "Y":
    tagObject[__FROZEN_CHECK_NAME[1]] = True


def process_deviation_check(tagObject, tagInfor):
  print(tagInfor)
  if __DEVIATION_CHECK_NAME[0] in tagObject:
    if tagInfor[__DEVIATION_CHECK_NAME[0]] == "":
      return
    tagObject[__DEVIATION_CHECK_NAME[1]] = tagInfor[__DEVIATION_CHECK_NAME[0]]


def process_control_logic_check(tagObject, tagInfor):
  if __CONTROL_LOGIC_CHECK_NAME[0] in tagObject:
    if tagInfor[__CONTROL_LOGIC_CHECK_NAME[0]] == "":
      return
    tagObject[__CONTROL_LOGIC_CHECK_NAME[1]] = tagInfor[__CONTROL_LOGIC_CHECK_NAME[0]]


def process_mp_startup(tagObject, tagInfor):
  if __MP_STARTUP[0] in tagObject:
    if tagInfor[__MP_STARTUP[0]] == "x":
      tagObject[__MP_STARTUP[1]] = True
    else:
      tagObject[__MP_STARTUP[1]] = False


def add_tag_info(tags, tagInfor):
  tagName = tagInfor["phd_tag"]
  if tagName not in tags:
    tags[tagName] = {}
  tagObject = tags[tagName]
  # process_description(tagObject, tagInfor)
  process_nan_check(tagObject, tagInfor)
  process_overange_check(tagObject, tagInfor)
  process_irv_check(tagObject, tagInfor)
  process_roc_check(tagObject, tagInfor)
  process_frozen_check(tagObject, tagInfor)
  process_deviation_check(tagObject, tagInfor)
  process_control_logic_check(tagObject, tagInfor)
  process_description(tagObject, tagInfor)
  process_mp_startup(tagObject, tagInfor)
  return tags[tagName]


def transform(devices):
  outputDevices = []
  for deviceName, deviceTags in devices.items():
    tags = []
    for tagName, detail in deviceTags.items():
      thisTag = {"tag_number": tagName, "checks": {key: detail[key] for key in detail if key != "description" and key != "mp_startup"}}
      if "description" in detail:
        thisTag["description"] = detail["description"]
      if "mp_startup" in detail:
        thisTag["mp_startup"] = detail["mp_startup"]
      tags.append(thisTag)
    thisDevice = {"name": deviceName, "label": deviceName, "tags": tags}
    outputDevices.append(thisDevice)
  return outputDevices


def add_deviation_checks(deviation_checks, name):
  if name not in deviation_checks and name != "":
    deviation_checks[name] = []


def add_deviation_check_members(deviation_checks, row):
  if row[__DEVIATION_CHECK_NAME[0]] in deviation_checks:
    deviation_checks[row[__DEVIATION_CHECK_NAME[0]]].append(row["phd_tag"])


def add_control_logic_check_members(control_logic_checks, row):
  if row[__CONTROL_LOGIC_CHECK_NAME[0]] in control_logic_checks:
    control_logic_checks[row[__CONTROL_LOGIC_CHECK_NAME[0]]].append(row["phd_tag"])


def add_control_logic_checks(control_logic_checks, name):
  if name not in control_logic_checks and name != "":
    control_logic_checks[name] = []


def main():
  data, output_file_name = itemgetter("data", "output_file_name")(init())
  devices = {}
  deviation_checks = {}
  control_logic_checks = {}
  for row in data:
    # PARSE DATA AND POPULATE INTO devices
    deviceTags = add_device_tags(devices, row["group"])
    add_tag_info(deviceTags, row)
    # ADD name of deviation_checks
    add_deviation_checks(deviation_checks, row[__DEVIATION_CHECK_NAME[0]])
    # ADD name of control_logic_checks
    add_control_logic_checks(control_logic_checks, row[__CONTROL_LOGIC_CHECK_NAME[0]])

  for row in data:
    # ADD members for each deviation_checks
    add_deviation_check_members(deviation_checks, row)
    # ADD members for each control_logic_checks
    add_control_logic_check_members(control_logic_checks, row)

  # NOW , WE DUMP devices
  outputObj = transform(devices)
  with open(output_file_name, "w") as output_file:
    yaml.dump({"devices": outputObj, "deviation_checks": deviation_checks, "control_logic_checks": control_logic_checks}, output_file)


if __name__ == '__main__':
  main()
