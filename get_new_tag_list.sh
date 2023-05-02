#!/bin/bash
wget --no-check-certificate -O assets/files/lip_tag_list.csv "https://docs.google.com/spreadsheets/d/1SqS6YiJbj5n0lR8kKX7Erin6nJGZcBES/export?format=csv"
python my_parser.py -i assets/files/lip_tag_list.csv -o assets/files/lip-tags.yaml
python parse_temp.py -i assets/files/lip_tag_list.csv -o assets/files/lip-tag-specs.yaml
wget --no-check-certificate -O assets/files/tag_list.csv "https://docs.google.com/spreadsheets/d/1cxeznYGs9TyLDVdX3UbDx91Vcm539jho5UkiiiXDxmk/export?format=csv"
python my_parser.py -i assets/files/tag_list.csv -o assets/files/tags.yaml
python parse_temp.py -i assets/files/tag_list.csv -o assets/files/tag-specs.yaml
