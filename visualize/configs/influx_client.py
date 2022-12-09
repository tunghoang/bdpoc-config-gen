from os import path,environ

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

client = InfluxDBClient.from_config_file(environ['INFLUX_CONFIG_FILE'] or "assets/files/config.ini")

write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()
