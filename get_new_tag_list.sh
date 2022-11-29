#!/bin/bash
wget --no-check-certificate -O assets/files/tag_list.csv "https://docs.google.com/spreadsheets/d/1cxeznYGs9TyLDVdX3UbDx91Vcm539jho5UkiiiXDxmk/export?gid=1926030884&format=csv"
python parser.py -i assets/files/tag_list.csv -o assets/files/tags.yaml
python parse_temp.py