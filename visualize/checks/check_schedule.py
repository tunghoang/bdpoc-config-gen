import schedule
import pandas as pd
from ..influx_utils import *

current_data = pd.DataFrame()

def job():
    print("job")

schedule.every(1).second.do(job)

while True:
    schedule.run_pending()