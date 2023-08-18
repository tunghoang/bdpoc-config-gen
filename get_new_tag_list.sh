#!/bin/bash

function process_tag_list {
  wget --no-check-certificate -O assets/files/$1 $2
  python my_parser.py -i assets/files/$1 -o assets/files/${3}s.yaml
  python parse_temp.py -i assets/files/$1 -o assets/files/${3}-specs.yaml
}
device=$1
if [ $device == 'lip' ]; then
process_tag_list lip_tag_list.csv "https://docs.google.com/spreadsheets/d/1SqS6YiJbj5n0lR8kKX7Erin6nJGZcBES/export?format=csv" lip-tag
fi

if [ $device == 'mp' ]; then
process_tag_list tag_list.csv "https://docs.google.com/spreadsheets/d/1cxeznYGs9TyLDVdX3UbDx91Vcm539jho5UkiiiXDxmk/export?format=csv" tag
fi

if [ $device == 'mr4100' ] ; then
process_tag_list mr4100_tag_list.csv "https://docs.google.com/spreadsheets/d/1EBdH5ASmEP6pWhqJg7Rjiuk5pobK4JkQ/export?format=csv" mr4100-tag
fi

if [ $device == 'mr4110' ] ; then
process_tag_list mr4110_tag_list.csv "https://docs.google.com/spreadsheets/d/1EIh-Q9WS59CgAg183_DWCDMEsB-93zoK/export?format=csv" mr4110-tag
fi

if [ $device == 'glycol' ] ; then
process_tag_list glycol_tag_list.csv "https://docs.google.com/spreadsheets/d/1dfEolAi861B7c7qOlgT_aV4kbtKDnvN3/export?format=csv" glycol-tag
fi

#wget --no-check-certificate -O assets/files/lip_tag_list.csv "https://docs.google.com/spreadsheets/d/1SqS6YiJbj5n0lR8kKX7Erin6nJGZcBES/export?format=csv"
#python my_parser.py -i assets/files/lip_tag_list.csv -o assets/files/lip-tags.yaml
#python parse_temp.py -i assets/files/lip_tag_list.csv -o assets/files/lip-tag-specs.yaml

#wget --no-check-certificate -O assets/files/tag_list.csv "https://docs.google.com/spreadsheets/d/1cxeznYGs9TyLDVdX3UbDx91Vcm539jho5UkiiiXDxmk/export?format=csv"
#python my_parser.py -i assets/files/tag_list.csv -o assets/files/tags.yaml
#python parse_temp.py -i assets/files/tag_list.csv -o assets/files/tag-specs.yaml

#wget --no-check-certificate -O assets/files/mr4100_tag_list.csv "https://docs.google.com/spreadsheets/d/1EBdH5ASmEP6pWhqJg7Rjiuk5pobK4JkQ/export?format=csv"
#python my_parser.py -i assets/files/mr4100_tag_list.csv -o assets/files/mr4100-tags.yaml
#python parse_temp.py -i assets/files/mr4100_tag_list.csv -o assets/files/mr4100-tag-specs.yaml

#wget --no-check-certificate -O assets/files/mr4110_tag_list.csv "https://docs.google.com/spreadsheets/d/1EIh-Q9WS59CgAg183_DWCDMEsB-93zoK/export?format=csv"
#python my_parser.py -i assets/files/mr4110_tag_list.csv -o assets/files/mr4110-tags.yaml
#python parse_temp.py -i assets/files/mr4110_tag_list.csv -o assets/files/mr4110-tag-specs.yaml

#wget --no-check-certificate -O assets/files/glycol_tag_list.csv "https://docs.google.com/spreadsheets/d/1EIh-Q9WS59CgAg183_DWCDMEsB-93zoK/export?format=csv"
#python my_parser.py -i assets/files/glycol_tag_list.csv -o assets/files/glycol-tags.yaml
#python parse_temp.py -i assets/files/glycol_tag_list.csv -o assets/files/glycol-tag-specs.yaml
