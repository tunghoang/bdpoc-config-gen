import csv
import sys

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