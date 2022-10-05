from visualize.configs.module_loader import *
from visualize.configs.Query import Query
from configs.influx_client import client
from configs.constants import BUCKET, ORG

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
    table = None
    if table_mode == "thin":
        table = client.query_api().query_data_frame(query, org=ORG)
        if not table.empty:
            # FORMAT TABLE
            # Add missing tags
            no_data_tags = [tag for tag in st.session_state["tags"] if tag not in table["_field"].values]
            missing_tags_df = pd.DataFrame({"_field": no_data_tags, "_time": [table["_time"][0] for _ in no_data_tags]})
            table = pd.concat([missing_tags_df, table], join="outer")
    elif table_mode == "fat":
        table = client.query_api().query_data_frame(pivot_query, org=ORG)
        if not table.empty:
            # FORMAT TABLE
            # Add missing tags
            no_data_tags = [tag for tag in st.session_state["tags"] if tag not in table.columns]
            has_data_tags = [tag for tag in st.session_state["tags"] if tag in table.columns]
            for tag in no_data_tags:
                table[tag] = table[has_data_tags[0]] = np.nan
    else:
        raise Exception("Unknown table mode")
    if "_time" in table:
        table["_time"] = table["_time"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))
    return table
