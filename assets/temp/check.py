class Check:
	def __init__(self):
		self.nan_check = None
		self.overange_check = None
		self.irv_check = None
		self.roc_check = None

	def to_dict(self):
		listing = {}
		if self.nan_check is not None:
			listing["nan_check"] = self.nan_check
		if self.overange_check is not None:
			listing["overange_check"] = self.overange_check
		if self.irv_check is not None:
			listing["irv_check"] = self.irv_check
		if self.roc_check is not None:
			listing["roc_check"] = self.roc_check
		return listing