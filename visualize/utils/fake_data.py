import random

import pandas as pd

def test(t):
  #t = t.reset_index()
  print(t)
  print("===========")
  size = t["derivative"].size
  pos = [(int(size / 5)) * x for x in range(1, 5)]
  prev = 0
  for idx, p in enumerate(pos):
    if idx == 0:
      t.loc[0:p, "derivative"] = 0
      prev = p
    elif idx == 1:
      t.loc[prev:p, "derivative"] = random.uniform(0, 2)
      prev = p
    elif idx == 2:
      t.loc[prev:p, "derivative"] = 0
      prev = p
    elif idx == 3:
      t.loc[prev:p, "derivative"] = random.uniform(-2, 0)
      prev = p
  t.loc[prev:size - 1, "derivative"] = 0
  return t


def fake_mp_startup(table: pd.DataFrame):
  #tables = table.groupby("_field").apply(test)
  size = table["derivative"].size
  pos = [(int(size / 5)) * x for x in range(1, 5)]
  prev = 0
  for idx, p in enumerate(pos):
    if idx == 0:
      table.loc[0:p, "derivative"] = 0
      prev = p
    elif idx == 1:
      table.loc[prev:p, "derivative"] = random.uniform(0, 2)
      prev = p
    elif idx == 2:
      table.loc[prev:p, "derivative"] = 0
      prev = p
    elif idx == 3:
      table.loc[prev:p, "derivative"] = random.uniform(-2, 0)
      prev = p
  table.loc[prev:size - 1, "derivative"] = 0
  #return tables.reset_index(drop=True)
  return table