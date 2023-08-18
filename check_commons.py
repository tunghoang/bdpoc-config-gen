from influx import Influx
from datetime import datetime, timedelta
from pytz import timezone

def runningIndicator(device='mp'):
  RUNNING_INDICATORS = {
    'mp': "HT_KM_2180.AND_RUNNING.OUT",
    'lip': "HT_KM_2110.AND_RUNNING.OUT",
    #'mr4100': 'HT_II_4107A.PV',
    'mr4100': 'HT_M_4100.PV',
    #'mr4110': 'HT_II_4107B.PV',
    'mr4110': 'HT_M_4110.PV'
  }
  return RUNNING_INDICATORS.get(device, None)

def is_on(value, tdelta, device='mp'):
  return value == "ON" and (tdelta.seconds > 10 * 60)
  #if device in ("mp", "lip"):
  #  return value == "ON" and (tdelta.seconds > 10 * 60)
  #if device in ("mr4100", "mr4110"):
  #  print("+++++++++++",value, value > 1.0)
  #  return value > 1.0

def is_running(device='mp'):
  field = runningIndicator(device)
  if field is None:
    return True
  df = Influx().setDebug(True).from_now(60*24*10).addField(field).setRate(None).setTail(2).asDataFrame()
  value = df._value[1]
  time = df._time[1]
  tdelta = datetime.now(timezone("Asia/Ho_Chi_Minh")) - time
  return is_on(value, tdelta, device=device)
