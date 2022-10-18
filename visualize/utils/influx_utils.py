from configs.constants import (BUCKET, CHECK_BUCKET, MONITORING_AGG_WINDOW, MONITORING_BUCKET, MONITORING_FIELD, MONITORING_MEASUREMENT, MONITORING_PERIOD, PIVOT)
from configs.module_loader import *
from configs.Query import Query
from services.influx_services import execute, get_check, get_database

warnings.simplefilter("ignore", MissingPivotFunction)


def query_raw_data(time: int, device: str, tags: list = [], interpolated: bool = False, missing_data: str = "NaN") -> DataFrame:
  if (not device) or (len(tags) == 0):
    return DataFrame()
  query = Query().from_bucket(BUCKET).range(time).filter_measurement(device).filter_fields(tags).keep_columns("_time", "_value", "_field")
  query = query.aggregate_window(True if missing_data == "NaN" else False).to_str()
  # print(query)
  pivot_query = Query().from_bucket(BUCKET).range(time).filter_measurement(device).filter_fields(tags).keep_columns("_time", "_value", "_field").aggregate_window(True).pivot("_time", "_field", "_value").to_str()
  table = get_database(pivot_query if PIVOT else query)
  if interpolated:
    test = table["_time"]
    table = table.drop(columns=["_time", "_start", "_stop"]).interpolate(method='linear', limit_direction='both', axis=0).assign(_time=test)
  return table


def query_check_data(time: int, device: str, tags: list = [], check_mode='none') -> DataFrame:
  if (not device) or (len(tags) == 0) or check_mode == 'none':
    return DataFrame()
  query = Query().from_bucket(CHECK_BUCKET).range(time)
  if check_mode != 'all':
    query.filter_measurement(check_mode)
  query = query.filter_fields(tags).to_str()
  table = get_check(query)
  if table.empty:
    assert Exception("No data found")
  return table


def dataframe_to_dictionary(df, measurement):
  df["_time"] = to_datetime(df['_time'], errors='coerce').astype(np.int64)
  lines = [{"measurement": f"{measurement}", "tags": {"device": row["_measurement"]}, "fields": {row["_field"]: float(row["_value"])}, "time": row["_time"]} for _, row in df.iterrows() if row["_value"] != 0 and not math.isnan(row["_value"])]
  return lines


def collector_status() -> float:
  query = Query().from_bucket(MONITORING_BUCKET).range(MONITORING_PERIOD).filter_measurement(MONITORING_MEASUREMENT).filter_fields([MONITORING_FIELD]).aggregate_window(False, MONITORING_AGG_WINDOW).to_str()
  result = execute(query)
  return "{:.2f}".format(result)
