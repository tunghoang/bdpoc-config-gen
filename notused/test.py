import schedule
import time
import traceback
import logging
from visualize.configs.logger import check_logger
check_logger.setLevel(logging.INFO);
def job1():
  objs = [{"abc": 2, "def": 5}, {"abc": 2, "def": 5}]
  check_logger.info(f"job 1 {objs}")
  time.sleep(1)
  check_logger.info("job 1 done")

def job2():
  check_logger.info("job 2")
  try:
    call_some_func()
  except:
    check_logger.exception("This is exception")

schedule.every(10).seconds.do(job1)
schedule.every(5).seconds.do(job2)
while True:
  schedule.run_pending()
  time.sleep(0.5)
