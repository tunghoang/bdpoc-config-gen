import yaml
from config_gen import csv_to_array_full_objects

def parse_irv_levels(irv_string, tagInfo):
  if irv_string is None or len(irv_string) == 0:
    tagInfo['low3'] = None
    tagInfo['low2'] = None
    tagInfo['low'] = None
    tagInfo['high'] = None
    tagInfo['high2'] = None
    tagInfo['high3'] = None
  else:
    tokens = irv_string.split(',')
    tagInfo['low3'] = float(tokens[0])
    tagInfo['low2'] = float(tokens[1])
    tagInfo['low'] = float(tokens[2])
    tagInfo['high'] = float(tokens[3])
    tagInfo['high2'] = float(tokens[4])
    tagInfo['high3'] = float(tokens[5])

tags = csv_to_array_full_objects('tag_list.csv')

cleanTags = {  }
for tag in tags:
  tagInfo = {'device': tag['group'], 'description': tag['measuring_point'], 'unit': tag.get('unit', 'NA') }
  parse_irv_levels(tag['instrument_range_validation'], tagInfo)
  cleanTags[tag['phd_tag']] = tagInfo

print(cleanTags)
with open('tag-specs.yaml', 'w') as f:
  yaml.dump(cleanTags, f)
