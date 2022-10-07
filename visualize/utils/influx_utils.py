from configs.constants import BUCKET, ORG
from configs.influx_client import client
from configs.module_loader import *
from configs.Query import Query
from services.influx_services import get_database_by_table_mode

warnings.simplefilter("ignore", MissingPivotFunction)

def query_data(time: int, device: str, tags: list = [], interpolated: bool = False, missing_data: str = "NaN", table_mode: str = "thin") -> pd.DataFrame:
    if (not device) or (len(tags) == 0):
        return DataFrame()
    query = Query().from_bucket(BUCKET).range(time).filter_measurement(device).filter_fields(tags).keep_columns("_time", "_value", "_field")
    if interpolated:
        query = query.interpolate()
    query = query.aggregate_window(True if missing_data == "NaN" else False).to_str()
    # print(query)
    pivot_query = Query().from_bucket(BUCKET).range(time).filter_measurement(device).filter_fields(tags).keep_columns("_time", "_value", "_field").aggregate_window(True).pivot("_time", "_field", "_value").to_str()
    table = get_database_by_table_mode(table_mode, query if table_mode == "thin" else pivot_query)
    if "_time" in table:
        table["_time"] = table["_time"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))
    return table

def dataframe_to_dictionary(df, measurement):
    df["_time"] = pd.to_datetime(df['_time'], errors='coerce').astype(np.int64)
    lines = [{"measurement": f"{measurement}", "tags": {"device": row["_measurement"]}, "fields": {row["_field"]: float(row["_value"])}, "time": row["_time"]} for _, row in df.iterrows() if row["_value"] != 0 and not math.isnan(row["_value"])]
    return lines
