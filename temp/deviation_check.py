class DeviationCheck:
	def __init__(self, name, members):
		self.name = name
		self.members = members

	def to_dict(self):
		return {"name": self.name, "members": self.members}