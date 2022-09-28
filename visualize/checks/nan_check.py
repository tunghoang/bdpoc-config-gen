from module_loader import *

# def nan_check(df, tag, threshold=0):
# nanCnt = 0
# maxNaNCnt = 0
# for index, row in df.iterrows():
# if math.isnan(row["_value"]):
#     nanCnt += 1
# else:
#     maxNaNCnt = nanCnt if nanCnt > maxNaNCnt else maxNaNCnt
#     nanCnt = 0
# return maxNaNCnt > threshold

def nan_check_multi(df, tags=[], pivot=False):
    if df is None or df.empty or len(tags) == 0:
        return
    res = copy.deepcopy(df)
    if pivot:
        for tag in tags:
            res[tag] = [math.isnan(row[tag]) for _, row in df.iterrows()]
        return res
    res["_value"] = [math.isnan(row["_value"]) for _, row in df.iterrows()]
    return res
    # results = []
    # for tag in tags:
    #     results.append(nan_check(df, tag))
    # return results