from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate an API token from the "API Tokens Tab" in the UI
token = "FzdIUoaRS33_-8R_oHn7SuyNSsZkOKs8lvPvpp2-5Pbbw2AZOmKO1YYDiMJBeIUwaG1EHAEMboGriS9GVzCU1A=="
org = "BDPOC"
bucket = "datahub"

with InfluxDBClient(url="http://localhost:8086", token=token, org=org) as client:
	query = 'from(bucket: "datahub") |> range(start: -1m)'
	tables = client.query_api().query(query, org=org)
	for table in tables:
		for record in table.records:
			print(record)
