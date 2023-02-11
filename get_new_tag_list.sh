#!/bin/bash
wget --no-check-certificate -O assets/files/lip_tag_list.csv "https://docs.google.com/spreadsheets/d/1yjwfpEtGM78mkXdnskUaU9CsOQZaGWuF/export?gid=1476496608&format=csv"
python my_parser.py -i assets/files/lip_tag_list.csv -o assets/files/lip_tags.yaml
# python parse_temp.py