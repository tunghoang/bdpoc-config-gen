from module_loader import *

def nan_check(df, tags=[], pivot=False):
    if df is None or df.empty or len(tags) == 0:
        return
    res = copy.deepcopy(df)
    if pivot:
        for tag in tags:
            if (tag in res.columns):
                res[tag] = [1 if math.isnan(row[tag]) else 0 for _, row in df.iterrows()]
        return res
    res["_value"] = [1 if math.isnan(row["_value"]) else 0 for _, row in df.iterrows()]
    return res