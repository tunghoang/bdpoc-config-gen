import smtplib, ssl
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

from visualize.configs.bdpoc_info import DEVICE_INFO

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

def email_targets(email_type, device = 'MP', testing=False):
  if testing:
    return ['tung.hoang@gmail.com']

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

def urgentMail(urgents, start, end, device="mp", tagDict={}, testing=False):
  sendMail = SendMail(template_dir="emails/")
  sendMail.formatAndSend(email_targets('urgent', device=device, testing=testing), 'urgent', events=urgents, start=start, end=end, device=device, tagDict=tagDict, DEVICE_INFO=DEVICE_INFO)

def wetGasSealMail(seals, start, end, tagDict={}, device="lip", testing=False):
  sendMail = SendMail(template_dir="emails/")
  sendMail.formatAndSend(email_targets('wetseals', device=device, testing=testing), 'wetseals', seals=seals, start=start, end=end, tagDict=tagDict, DEVICE_INFO=DEVICE_INFO)

def criticalMail(criticals, start, end, device="mp", tagDict={}, testing=False):
  sendMail = SendMail(template_dir="emails/")
  sendMail.formatAndSend(email_targets('critical', device=device, testing=testing), 'critical', events=criticals, start=start, end=end, device=device, tagDict=tagDict, DEVICE_INFO=DEVICE_INFO)

def transientMail(action, start, end, device="mp", tagDict={}, testing=False):
  sendMail = SendMail(template_dir="emails/")
  sendMail.formatAndSend(email_targets('transient', device=device, testing=testing), 'transient', action=action, start=start, end=end, device=device, tagDict=tagDict, DEVICE_INFO=DEVICE_INFO)

def dailyMail(nan=[], overange=[], roc=[], irv=[], tagDict={}, device="mp", start=None, end=None, testing=False):
  sendMail = SendMail(template_dir="emails/")
  sendMail.formatAndSend(email_targets('daily', device=device, testing=testing), 'daily', device=device, nan=nan, overange=overange, roc=roc, irv=irv, start=start, end=end, tagDict=tagDict, DEVICE_INFO=DEVICE_INFO)

def datasourceMail(failed_sources, checkTime, testing=False):
  sendMail = SendMail(template_dir="emails/")
  sendMail.formatAndSend(['tung.hoang@gmail.com', 'cuonglv@biendongpoc.vn', 'trungnt@biendongpoc.vn', 'trungtn@biendongpoc.vn'], "datasource", sources=failed_sources, start=checkTime, DEVICE_INFO=DEVICE_INFO)
