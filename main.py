import csv
import yaml
import getopt
import sys

_YAML_FILE = "tags.yaml"
_TAG_LIST_FILE = "tag_list.csv"

class Tag:
	def __init__(self, name, label):
		self.name = name
		self.label = label
		self.checks = [{"type": "nan_check"}, {"type": "overange_check"}, {"type": "irv_check"}, {"type": "frozen_check"}, {"type": "roc_check"}]

	def __repr__(self):
		return f"name: {self.name}, label: {self.label}, checks: {self.checks}"

class Device:
	def __init__(self, name, label):
		self.name = name
		self.label = label
		self.tags = None

	def __repr__(self):
		return f"name: {self.name}, label: {self.label}, tags: {self.tags}"

def csv_to_array_full_objects(fpath):
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
			result.append(content)
	result.sort(key=lambda x: x["group"])
	return iter(result)

def usage():
	print("Usage:")
	print("python main.py [option]")
	print("\t-i, --input\t\tInput file")
	print("\t-o, --output\t\tOutput file")
	print("\t-h, --help\t\tPrint this help")

def main():
	file_input = _TAG_LIST_FILE
	file_output = _YAML_FILE
	try:
		options, _remainder = getopt.getopt(sys.argv[1:], "i:o:h", ["input=", "output=", "help"])
		if (len(options) == 0):
			check_input = input("Enter your csv input file (tag_list.csv): ")
			if (check_input != ""): file_input = check_input
			check_output = input("Enter your yaml output file (tags.yaml): ")
			if (check_output != ""): file_output = check_output
	except getopt.GetoptError as err:
		print(err)
		usage()
		sys.exit(2)
	for opt, arg in options:
		if opt in ("-i", "--input"):
			file_input = arg
		elif opt in ("-o", "--output"):
			file_output = arg
		elif opt in ("-h", "--help"):
			usage()
			sys.exit()
		else:
			assert False, "unhandled option"
	data = csv_to_array_full_objects(file_input)
	# keys = list(data[0].keys())
	devices = {"devices": []}
	names = set()
	while True:
		row = next(data, None)
		if row is None: break
		if row["group"] not in names:
			names.add(row["group"])
			device = Device(row["group"], row["group"])
			tags = list()
		while True:
			if row is None: break
			if row["group"] not in names: break
			tag = Tag(row["tag_no."], row["measuring_point"])
			tags.append({"name": tag.name, "label": tag.label, "checks": tag.checks})
			row = next(data, None)
		device.tags = tags
		devices["devices"].append({"name": device.name, "label": device.label, "tags": device.tags})

	# print(devices)

	with open(file_output, 'w') as file:
		yaml.dump(devices, file)

if __name__ == '__main__':
	main()