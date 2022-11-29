import csv
import re
import string
import sys

# from raw_csv import RawCsv


def csv_to_array_full_objects(fpath: string) -> list:
  """Convert csv file to an array of objects

	Args:
			fpath (string): Path to csv file

	Returns:
			list[RawCsv]: List of RawCsv objects
	"""
  result = list()
  try:
    with open(fpath, encoding='utf-8') as file:
      file_read = csv.reader(file)
      array = list(file_read)
  except FileNotFoundError as err:
    print(err)
    sys.exit(2)
  for row_index, row in enumerate(array):
    if row_index == 0:
      data_headings = list()
      for heading in row:
        fixed_heading = heading.lower().replace(" ", "_").replace("-", "").replace("\n", "_")
        data_headings.append(fixed_heading)
    else:
      content = dict()
      for cell_index, cell in enumerate(row):
        content[data_headings[cell_index]] = cell
      if (content["not_now"] == ""):
        result.append(content)
  return result


__irv_check_param_names = ("low_low", "low", "high", "high_high")


def irv_param_name(idx):
  return __irv_check_param_names[idx]


def calculate_check(str, num_params):
  check_params = {}
  print(str)
  if num_params == 2:
    overange_checks = re.sub("[\[\] ]", "", str).split(",")
    for index, num in enumerate(overange_checks):
      if (index == 0):
        check_params["min"] = float(num)
      elif (index == 1):
        check_params["max"] = float(num)
      if (len(check_params) == 0):
        check_params["min"] = None
      if (len(check_params) == 1):
        check_params["max"] = None
  elif num_params == 4:
    irv_checks = str.split(',')
    if len(irv_checks) == 4:
      for index, num in enumerate(irv_checks):
        if num == "_":
          check_params[irv_param_name(index)] = None
        else:
          check_params[irv_param_name(index)] = float(num)
  return check_params


# def format_device(data, name):
#   device = Device(row["group"], row["group"])
#   tags = list()
#   deviation_checks = list()
#   prev = None
#   for row in data:
#     if row["group"] == name:
#       tag_number = row["phd_tag"]
#       measuring_point = row["measuring_point"]
#       tag = Tag(tag_number, measuring_point)
#       check = Check(None, None, None, None)
#       if row["nan_check"] == "Y":
#         check.nan_check = True
#       if row["overange_check"] != "":
#         check.overange_check = calculate_check(row["overange_check"], 2)
#       if row["instrument_range_validation"] != "":
#         check.irv_check = calculate_check(row["instrument_range_validation"], 4)
#       if row["rate_of_change_check"] != "":
#         check.roc_check = row["rate_of_change_check"]
#       tag.checks = check
#       tags.append(tag.to_dict())
#       check_tag = get_deviation_check_num(row)
#       if check_tag != None:
#         if check_tag != prev:
#           deviation_checks.append({"name": check_tag, "members": [row["phd_tag"]]})
#           prev = check_tag
#         else:
#           for deviation_check in deviation_checks:
#             if (deviation_check["name"] == check_tag):
#               deviation_check["members"].append(row["phd_tag"])
#   device.tags = tags
#   return {"device": device, "deviation_checks": deviation_checks}


def get_deviation_check_num(row):
  if (row["cross_ref.__(deviation_check)__number"] == ""):
    return None
  return row["cross_ref.__(deviation_check)__number"]


def check_row_index(data, check_index):
  for index, _ in enumerate(data):
    if (index == check_index):
      return True
    if (index > check_index):
      return False
