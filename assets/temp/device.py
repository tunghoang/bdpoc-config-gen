class Device:
	def __init__(self, name, label):
		self.name = name
		self.label = label
		self.tags = None

	def __repr__(self):
		return f"name: {self.name}, label: {self.label}, tags: {self.tags}"

	def to_dict(self):
		return {"name": self.name, "label": self.label, "tags": self.tags}

	def check_device(self):
		if self.tags == None or len(self.tags) == 0:
			return False
		return True