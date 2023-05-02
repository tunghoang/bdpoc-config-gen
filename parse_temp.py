import yaml
import argparse
from config_gen import csv_to_array_full_objects

def __isFloat(s):
  try:
    v = float(s)
    return True
  except:
    return False


def __fill_missing(array):
  count = 0
  result = []
  currentVal = None
  for a in array:
    if __isFloat(f"{a}"):
      currentVal = float(a)
      if count > 0:
        result = result + [currentVal] * count
        count = 0
      result.append(currentVal)
    else:
      count = count + 1
  if count > 0:
    result = result + [currentVal] * count
  return result


def myfloat(s):
  try:
    return float(s)
  except:
    return "NA"


def parse_irv_levels(irv_string, tagInfo, verbose=False):
  if irv_string is None or len(irv_string) == 0:
    tagInfo['low3'] = "NA"
    tagInfo['low2'] = "NA"
    tagInfo['low'] = "NA"
    tagInfo['high'] = "NA"
    tagInfo['high2'] = "NA"
    tagInfo['high3'] = "NA"
  else:
    tokens = [x for x in irv_string.split(',')]
    if verbose:
      print(tokens)
    tokens = __fill_missing(tokens)
    if verbose:
      print(tokens)
    if len(tokens) == 6:
      tagInfo['low3'] = myfloat(tokens[0])
      tagInfo['low2'] = myfloat(tokens[1])
      tagInfo['low'] = myfloat(tokens[2])
      tagInfo['high'] = myfloat(tokens[3])
      tagInfo['high2'] = myfloat(tokens[4])
      tagInfo['high3'] = myfloat(tokens[5])
    else:
      tagInfo['low3'] = "NA"
      tagInfo['low2'] = "NA"
      tagInfo['low'] = "NA"
      tagInfo['high'] = "NA"
      tagInfo['high2'] = "NA"
      tagInfo['high3'] = "NA"


parser = argparse.ArgumentParser(prog='Parse tag-specs',
                    description='parse tag list into tag-specs',
                    epilog='')

parser.add_argument("-i", "--input")
parser.add_argument("-o", "--output")

args = parser.parse_args()

print("args", args)
inputFile = args.input or 'assets/files/mp_startup.csv' 
outputFile = args.output or 'assets/files/tag-specs.yaml'
print(inputFile, outputFile)
tags = csv_to_array_full_objects(inputFile)

cleanTags = {}
for tag in tags:
  tagInfo = {
    'device': tag['group'], 
    'description': tag['measuring_point'], 
    'unit': tag.get('unit', 'NA'), 
    'mp_startup': True if tag['mp_startup'] == "x" or tag['critical'] == 'X' else False,
    'critical': True if tag['critical'] == "x" or tag['critical'] == 'X' else False
  }
  parse_irv_levels(tag['instrument_range_validation'], tagInfo)
  cleanTags[tag['phd_tag']] = tagInfo

with open(outputFile, 'w') as f:
  yaml.dump(cleanTags, f)
