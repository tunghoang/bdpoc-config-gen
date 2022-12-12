import schedule
import time

def job1():
  print("Job 1")
  time.sleep(12)
  print("Job1 done")

def job2():
  print("Job 2")

schedule.every(10).seconds.do(job1)
schedule.every(5).seconds.do(job2)
while True:
  print(".", end='')
  schedule.run_pending()
  time.sleep(0.5)
