from typing import TypedDict

class RawCsv(TypedDict):
	"no.": str
	"group": str
	"tag_no": str
	"phd_tag": str
	"measuring_point": str
	"nan_check": str
	"overange_check": str
	"instrument_range_validation": str
	"frozen_check_(5_min_configurable)": str
	"rate_of_change_check": str
	"travelling_check": str
	"deviation_check": str
	"cross_ref._(deviation_check)__tagname": str
	"control_logic_check__tagname": str
	"remark_(điều_kiện_bình_thường)": str
	"not_now": str