from datetime import datetime
import streamlit as st

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json
from pandas import DataFrame

import warnings
from influxdb_client.client.warnings import MissingPivotFunction
warnings.simplefilter("ignore", MissingPivotFunction)

bucket = "datahub"
org = "BDPOC"
token = "FzdIUoaRS33_-8R_oHn7SuyNSsZkOKs8lvPvpp2-5Pbbw2AZOmKO1YYDiMJBeIUwaG1EHAEMboGriS9GVzCU1A=="
# org = "BDPOC"
# bucket = "datahub"

@st.experimental_singleton
def get_influx_client():
	return InfluxDBClient(url="http://localhost:8086", token=token, org=org)

def query_data(time, device, tags=[], windowPeriod='10s', interpolated=False, missing_data="NaN"):
	if ( not device ) or (len(tags) == 0):
		return DataFrame()
	client = get_influx_client()
	query = f'''import "interpolate"
        from(bucket: "datahub")
            |> range(start: -{time})
            |> filter(fn: (r) => r._measurement == {json.dumps(device)})
            |> filter(fn: (r) => contains(value: r._field, set: {json.dumps(tags)}))
            |> keep(columns: ["_time", "_value", "_field"])
            {"|> interpolate.linear(every: 1s)" if interpolated else ""}
            |> aggregateWindow(every: 1s, fn: mean, createEmpty: {"true" if missing_data=="NaN" else "false"})
            |> yield(name: "mean")
                        //|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''
	query1 = f'''
        from(bucket: "datahub")
            |> range(start: -{time})
            |> filter(fn: (r) => r._measurement == {json.dumps(device)})
            |> filter(fn: (r) => contains(value: r._field, set: {json.dumps(tags)}))
            |> keep(columns: ["_time", "_value", "_field"])
                        //|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''
	tables = client.query_api().query_data_frame(query, org=org)
	return tables
