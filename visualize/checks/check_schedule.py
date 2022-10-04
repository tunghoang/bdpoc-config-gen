import schedule
import pandas as pd
from ..influx_utils import *
from Query import Query

client = InfluxDBClient.from_config_file("../config.ini")
current_data = pd.DataFrame()

def job():
	query = Query().from_bucket(bucket).range("1m").aggregate_window(True).pivot("_time", "_field", "_value").to_str()
	table = client.query_api().query_data_frame(query, org=org)
	return table

schedule.every(1).minute.do(job)

while True:
	schedule.run_pending()
