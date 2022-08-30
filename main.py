import csv
import yaml

_YAML_FILE = r"input-tags.yaml"
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
	with open(fpath, encoding='utf-8') as file:
		file_read = csv.reader(file)
		array = list(file_read)
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

def main():
	data = csv_to_array_full_objects(_TAG_LIST_FILE)
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

	with open(_YAML_FILE, 'w') as file:
		yaml.dump(devices, file)

if __name__ == '__main__':
	main()