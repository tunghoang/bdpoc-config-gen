class Tag:
	def __init__(self, tag_number, measuring_point):
		self.tag_number = tag_number
		self.measuring_point = measuring_point
		self.check = {}

	def __repr__(self):
		return f"tag_number: {self.tag_number}, measuring_point: {self.measuring_point}, check: {self.check}"

	def to_dict(self):
		check = self.check.to_dict()
		if check == {}:
			return {"tag_number": self.tag_number, "measuring_point": self.measuring_point}
		return {"tag_number": self.tag_number, "measuring_point": self.measuring_point, "check": self.check.to_dict()}