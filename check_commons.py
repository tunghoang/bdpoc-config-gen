from influx import Influx

def runningIndicator(device='mp'):
  RUNNING_INDICATORS = {
    'mp': "HT_KM_2180.AND_RUNNING.OUT",
    'lip': "HT_KM_2110.AND_RUNNING.OUT"
  }
  return RUNNING_INDICATORS.get(device, None)

def is_running(device='mp'):
  field = runningIndicator(device)
  if field is None:
    return True
  df = Influx().setDebug(True).from_now(60*24*10).addField(field).setRate(None).setTail(2).asDataFrame()
  value = df._value[1]
  return value == "ON"
