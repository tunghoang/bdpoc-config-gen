import warnings

from configs.logger import check_logger
import numpy as np
import pandas as pd
import math

from configs.constants import RUL_WINDING_TEMP

Lambda =  math.log(2) / 10 

def winding_temp_regression(tag):
  file_name = RUL_WINDING_TEMP[tag]
  df = pd.read_csv(file_name)
  df['time'] = pd.to_datetime(df.time)
  df['year'] = df['time'].dt.year
  df['month'] = df['time'].dt.month
  df['day'] = df['time'].dt.day

  selected_cols = ['year']

  df1 = df[['temperature', *selected_cols]]
  df1 = df1[ (df1.temperature > 60) ]
  df1 = df1.groupby(selected_cols).mean()
  df1.reset_index(inplace=True)
  df1['tau'] = np.exp( -Lambda * (df1['temperature']) )

  df1['d_tau'] = df1.tau - df1.tau.shift(1) 
  df1['d_year'] = -1
  df1['R0'] = df1.d_year / df1.d_tau

  estR0 = df1.R0.mean()
  return estR0

def remaining_useful_life(tags, temps):
  return np.array([winding_temp_regression(tags[idx]) * math.exp( -Lambda * temps[idx]) for idx in range(len(tags))])

