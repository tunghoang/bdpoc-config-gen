import smtplib, ssl
import sqlite3
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

from visualize.configs.bdpoc_info import DEVICE_INFO
from visualize.configs.constants import EMAIL_PASSWORD
EMAIL_DB_FILE = "./state/email.db"

TEST_EMAILS = ['tung.hoang@gmail.com', 'trungnt@biendongpoc.vn', 'tuancs@biendongpoc.vn']

ADDITIONAL = "additional@biendongpoc.vn"
RES='res@biendongpoc.vn'
REE='ree@biendongpoc.vn'
CRE="cre@biendongpoc.vn"
FIELD_SUPV = 'fieldprodsupv@biendongpoc.vn'
TL_RES = 'ninhpa@biendongpoc.vn'
EnI_SUPV = 'E&ISupv@biendongpoc.vn'
ASSISTANT_EnI_SUPV = 'assistante&isupv@biendongpoc.vn'
MECHANICAL_SUPV = 'mechanicalsupv@biendongpoc.vn'
from bdpocmail import SendMail

EMAIL_TARGETS = {
  "mp": {
    "critical": [
      'oim@biendongpoc.vn', 
      'deputyoim@biendongpoc.vn', 
      'RES@biendongpoc.vn', 
      'Ree@biendongpoc.vn', 
      'CuongLV@biendongpoc.vn', 
      "NinhPA@biendongpoc.vn", 
      'e&isupv@biendongpoc.vn', 
      "assistante&isupv@biendongpoc.vn", 
      "fieldprodsupv@biendongpoc.vn", 
      "cre@biendongpoc.vn", 
      "pqpprodsupv@biendongpoc.vn", 
      "hiennv@biendongpoc.vn"
    ],
    "urgent":	[
      'oim@biendongpoc.vn', 
      'deputyoim@biendongpoc.vn', 
      'RES@biendongpoc.vn', 
      'Ree@biendongpoc.vn', 
      'CuongLV@biendongpoc.vn', 
      "NinhPA@biendongpoc.vn", 
      'e&isupv@biendongpoc.vn', 
      "assistante&isupv@biendongpoc.vn", 
      "fieldprodsupv@biendongpoc.vn", 
      "cre@biendongpoc.vn", 
      "pqpprodsupv@biendongpoc.vn", 
      "hiennv@biendongpoc.vn"
    ],
    "transient": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'RES@biendongpoc.vn',
      'Ree@biendongpoc.vn',
      'CuongLV@biendongpoc.vn'
    ], 
    "wetseals":	[],
    "datasource":	[],
    "daily": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'RES@biendongpoc.vn',
      'Ree@biendongpoc.vn',
      'CuongLV@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'hiennv@biendongpoc.vn'
    ],
    "vibration": []
  },
  "lip": {
    "critical": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'RES@biendongpoc.vn',
      'Ree@biendongpoc.vn',
      'CuongLV@biendongpoc.vn',
      'NinhPA@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'fieldprodsupv@biendongpoc.vn',
      'cre@biendongpoc.vn',
      'pqpprodsupv@biendongpoc.vn',
      'hiennv@biendongpoc.vn'
    ],
    "urgent":	[
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'RES@biendongpoc.vn',
      'Ree@biendongpoc.vn',
      'CuongLV@biendongpoc.vn',
      'NinhPA@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'fieldprodsupv@biendongpoc.vn',
      'cre@biendongpoc.vn',
      'pqpprodsupv@biendongpoc.vn',
      'hiennv@biendongpoc.vn'
    ],
    "transient": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'RES@biendongpoc.vn',
      'Ree@biendongpoc.vn',
      'CuongLV@biendongpoc.vn'
    ], 
    "wetseals":	[
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'RES@biendongpoc.vn',
      'Ree@biendongpoc.vn',
      'CuongLV@biendongpoc.vn',
      'fieldprodsupv@biendongpoc.vn',
      'cre@biendongpoc.vn',
      'pqpprodsupv@biendongpoc.vn',
      'hiennv@biendongpoc.vn'
    ],
    "datasource":	[],
    "daily": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'RES@biendongpoc.vn',
      'Ree@biendongpoc.vn',
      'CuongLV@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'hiennv@biendongpoc.vn'
    ],
    "vibration": []
  },
  "mr4100":{
    "critical": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'fieldprodsupv@biendongpoc.vn',
      'cre@biendongpoc.vn',
      'pqpprodsupv@biendongpoc.vn',
      'mechanicalsupv@biendongpoc.vn',
      'assistantmechsupv@biendongpoc.vn'
    ],
    "urgent":	[
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'fieldprodsupv@biendongpoc.vn',
      'cre@biendongpoc.vn',
      'pqpprodsupv@biendongpoc.vn',
      'mechanicalsupv@biendongpoc.vn',
      'assistantmechsupv@biendongpoc.vn'
    ],
    "transient": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'mechanicalsupv@biendongpoc.vn',
      'assistantmechsupv@biendongpoc.vn',
      'hiennv@biendongpoc.vn'
    ], 
    "wetseals":	[ ],
    "datasource":	[],
    "daily": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'mechanicalsupv@biendongpoc.vn',
      'assistantmechsupv@biendongpoc.vn',
      'hiennv@biendongpoc.vn'
    ],
    "vibration": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'fieldprodsupv@biendongpoc.vn',
      'cre@biendongpoc.vn',
      'pqpprodsupv@biendongpoc.vn',
      'mechanicalsupv@biendongpoc.vn',
      'assistantmechsupv@biendongpoc.vn'
    ]
  },
  "mr4110": {
    "critical": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'fieldprodsupv@biendongpoc.vn',
      'cre@biendongpoc.vn',
      'pqpprodsupv@biendongpoc.vn',
      'mechanicalsupv@biendongpoc.vn',
      'assistantmechsupv@biendongpoc.vn'
    ],
    "urgent":	[
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'fieldprodsupv@biendongpoc.vn',
      'cre@biendongpoc.vn',
      'pqpprodsupv@biendongpoc.vn',
      'mechanicalsupv@biendongpoc.vn',
      'assistantmechsupv@biendongpoc.vn'
    ],
    "transient": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'mechanicalsupv@biendongpoc.vn',
      'assistantmechsupv@biendongpoc.vn',
      'hiennv@biendongpoc.vn'
    ], 
    "wetseals":	[ ],
    "datasource":	[],
    "daily": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'mechanicalsupv@biendongpoc.vn',
      'assistantmechsupv@biendongpoc.vn',
      'hiennv@biendongpoc.vn'
    ],
    "vibration": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'fieldprodsupv@biendongpoc.vn',
      'cre@biendongpoc.vn',
      'pqpprodsupv@biendongpoc.vn',
      'mechanicalsupv@biendongpoc.vn',
      'assistantmechsupv@biendongpoc.vn'
    ]
  },
  "glycol": {
    "critical": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'fieldprodsupv@biendongpoc.vn',
      'cre@biendongpoc.vn',
      'pqpprodsupv@biendongpoc.vn',
      'mechanicalsupv@biendongpoc.vn',
      'assistantmechsupv@biendongpoc.vn'
    ],
    "urgent": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'fieldprodsupv@biendongpoc.vn',
      'cre@biendongpoc.vn',
      'pqpprodsupv@biendongpoc.vn',
      'mechanicalsupv@biendongpoc.vn',
      'assistantmechsupv@biendongpoc.vn'
    ],
    "transient": [],
    "wetseals": [],
    "datasource": [],
    "daily": [
      'oim@biendongpoc.vn',
      'deputyoim@biendongpoc.vn',
      'e&isupv@biendongpoc.vn',
      'assistante&isupv@biendongpoc.vn',
      'mechanicalsupv@biendongpoc.vn',
      'assistantmechsupv@biendongpoc.vn',
      'hiennv@biendongpoc.vn'
    ],
    "vibration": []
  }
}

def sms_store(events, severity, sent_date):
  '''sms_store: sent_mail_state store'''
  conn = sqlite3.connect(EMAIL_DB_FILE)
  sent_date_str = sent_date.strftime("%Y-%m-%d")
  records = []
  for e in events:
    if severity == "wetseal":
      records.append((sent_date_str, severity, e["Field"]))
    else:
      records.append( (sent_date_str, severity, f'{e["Field"]}#{"HHH" if e["Max"] >= e["HHH"] else "LLL"}') )

  cursor = conn.cursor()
  query = "INSERT into sent_mail (sent_date, severity, symptom) values(?, ?, ?)"
  cursor.executemany(query, records)
  conn.commit()

def sms_query(events, severity, sent_date):
  '''sms_query: sent_mail_state query'''
  conn = sqlite3.connect(EMAIL_DB_FILE)
  symptoms = [f"'{e['Field']}#{'HHH' if e['Max'] >= e['HHH'] else 'LLL'}'" for e in events]
  sent_date_str = sent_date.strftime("%Y-%m-%d")
  query = f"SELECT symptom from sent_mail WHERE sent_date = '{sent_date_str}' AND severity = '{severity}' AND symptom in ( {','.join(symptoms)} )"
  print(query)
  cursor = conn.cursor()
  cursor.execute(query)
  tags = [row[0].split("#")[0] for row in cursor]
  print(tags)
  return list(filter(lambda e: e["Field"] not in tags, events))

def email_targets(email_type, device = 'MP', testing=False):
  if testing:
    return TEST_EMAILS
  return EMAIL_TARGETS[device.lower()][email_type]
'''
  targets = []

  if email_type == 'urgent' or email_type == 'transient':
    targets += [RES, REE]
  elif email_type == 'critical':
    targets += [RES, REE, CRE, FIELD_SUPV, TL_RES]
  elif email_type == 'wesseals':
    targets += [RES, REE, EnI_SUPV, ASSISTANT_EnI_SUPV]
  elif email_type == 'daily':
    targets += [RES, REE, EnI_SUPV, ASSISTANT_EnI_SUPV]

  if device in ['mr4100', 'mr4110']:
    targets += [MECHANICAL_SUPV]

  targets += ['tung.hoang@gmail.com', 'cuonglv@biendongpoc.vn']
  return targets
'''

def urgentMail(urgents, start, end, device="mp", tagDict={}, testing=False):
  if len(urgents) == 0:
    return
  sms_store(urgents, "urgent", end)
  sendMail = SendMail(template_dir="emails/", password=EMAIL_PASSWORD)
  sendMail.formatAndSend(email_targets('urgent', device=device, testing=testing), 'urgent', events=urgents, start=start, end=end, device=device, tagDict=tagDict, DEVICE_INFO=DEVICE_INFO)

def wetGasSealMail(seals, start, end, tagDict={}, device="lip", testing=False):
  if len(seals) == 0:
    print("No event. Exit")
    return

  sms_store(seals, "wetseal", end)

  sendMail = SendMail(template_dir="emails/", password=EMAIL_PASSWORD)
  sendMail.formatAndSend(email_targets('wetseals', device=device, testing=testing), 'wetseals', seals=seals, start=start, end=end, tagDict=tagDict, DEVICE_INFO=DEVICE_INFO)

def criticalMail(criticals, start, end, device="mp", tagDict={}, testing=False):
  if len(criticals) == 0:
    print("No event. Exit");
    return
  sms_store(criticals, "critical", start)
  sendMail = SendMail(template_dir="emails/", password=EMAIL_PASSWORD)
  sendMail.formatAndSend(email_targets('critical', device=device, testing=testing), 'critical', events=criticals, start=start, end=end, device=device, tagDict=tagDict, DEVICE_INFO=DEVICE_INFO, testing=(device=='lip'))

def transientMail(action, start, end, device="mp", event_time=[], tagDict={}, testing=False):
  sendMail = SendMail(template_dir="emails/", password=EMAIL_PASSWORD)
  sendMail.formatAndSend(email_targets('transient', device=device, content_format="html", testing=testing), 'transient', action=action, start=start, end=end, device=device, tagDict=tagDict, event_time=event_time, DEVICE_INFO=DEVICE_INFO)

def dailyMail(nan=[], overange=[], roc=[], irv=[], tagDict={}, device="mp", start=None, end=None, testing=False):
  sendMail = SendMail(template_dir="emails/", password=EMAIL_PASSWORD)
  sendMail.formatAndSend(email_targets('daily', device=device, testing=testing), 'daily', content_format="html", device=device, nan=nan, overange=overange, roc=roc, irv=irv, start=start, end=end, tagDict=tagDict, DEVICE_INFO=DEVICE_INFO)

def datasourceMail(failed_sources, checkTime, testing=False):
  sendMail = SendMail(template_dir="emails/", password=EMAIL_PASSWORD)
  sendMail.formatAndSend(['tung.hoang@gmail.com', 'cuonglv@biendongpoc.vn', 'trungnt@biendongpoc.vn', 'trungtn@biendongpoc.vn', 'tuancs@biendongpoc.vn'], "datasource", sources=failed_sources, start=checkTime, DEVICE_INFO=DEVICE_INFO)

def vibrationMail(events, tagDict={}, device="mr4100", testing=False):
  sendMail = SendMail(template_dir="emails/", password=EMAIL_PASSWORD)
  sendMail.formatAndSend(
    email_targets('vibration', device=device, testing=testing), 
    "vibration", events=events, device=device, tagDict=tagDict, DEVICE_INFO=DEVICE_INFO
  )
