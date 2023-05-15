import smtplib, ssl
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

ADDITIONAL = "additional@biendongpoc.vn"
RES='res@biendongpoc.vn'
REE='ree@biendongpoc.vn'
CRE="cre@biendongpoc.vn"
FIELD_SUPV = 'fieldprodsupv@biendongpoc.vn'
TL_RES = 'ninhpa@biendongpoc.vn'
EnI_SUPV = 'E&ISupv@biendongpoc.vn'
ASSISTANT_EnI_SUPV = 'assistante&isupv@biendongpoc.vn'

from bdpocmail import SendMail

def urgentMail(urgents, start, end, device="mp", testing=False):
  sendMail = SendMail(template_dir="emails/")
  if testing:
    sendMail.formatAndSend(['tung.hoang@gmail.com', 'cuonglv@biendongpoc.vn', 'trungnt@biendongpoc.vn', 'hiennv@biendongpoc.vn'], 'urgent', events=urgents, start=start, end=end, device=device)
  else:
    sendMail.formatAndSend([RES, REE], 'urgent', events=urgents, start=start, end=end, device=device)

def wetGasSealMail(seals, start, end, testing=False):
  sendMail = SendMail(template_dir="emails/")
  if testing:
    sendMail.formatAndSend([
      'tung.hoang@gmail.com', 
      'cuonglv@biendongpoc.vn', 
      'trungnt@biendongpoc.vn', 
      'hiennv@biendongpoc.vn'
    ], 'wetseals', seals=seals, start=start, end=end)
  else:
    sendMail.formatAndSend([RES, REE, EnI_SUPV, ASSISTANT_EnI_SUPV], 'wetseals', seals=seals, start=start, end=end)

def criticalMail(criticals, start, end, device="mp", testing=False):
  sendMail = SendMail(template_dir="emails/")
  if testing:
    sendMail.formatAndSend(['tung.hoang@gmail.com', 'cuonglv@biendongpoc.vn', 'trungnt@biendongpoc.vn', 'hiennv@biendongpoc.vn'], 'critical', events=criticals, start=start, end=end, device=device)
  else:
    sendMail.formatAndSend([RES, REE, CRE, FIELD_SUPV, TL_RES], 'critical', events=criticals, start=start, end=end, device=device)

def transientMail(action, start, end, device="mp", testing=False):
  sendMail = SendMail(template_dir="emails/")
  if testting:
    sendMail.formatAndSend(['tung.hoang@gmail.com', 'cuonglv@biendongpoc.vn', 'trungnt@biendongpoc.vn', 'hiennv@biendongpoc.vn'], 'transient', action=action, start=start, end=end, device=device)
  else:
    sendMail.formatAndSend([RES, REE], 'transient', action=action, start=start, end=end, device=device)

def dailyMail(nan=[], overange=[], roc=[], irv=[], start=None, end=None):
  sendMail = SendMail(template_dir="emails/")
  sendMail.formatAndSend([RES, REE, EnI_SUPV, ASSISTANT_EnI_SUPV], 'daily', nan=nan, overange=overange, roc=roc, irv=irv, start=start, end=end)

def testDailyMail(nan=[], overange=[], roc=[], irv=[], start=None, end=None):
  sendMail = SendMail(template_dir="emails/")
  #sendMail.formatAndSend([RES, REE, EnI_SUPV, ASSISTANT_EnI_SUPV], 'daily', nan=nan, overange=overange, roc=roc, irv=irv, start=start, end=end)
  sendMail.formatAndSend(['tung.hoang@gmail.com', 'cuonglv@biendongpoc.vn', 'trungnt@biendongpoc.vn', 'hiennv@biendongpoc.vn'], 'daily', nan=nan, overange=overange, roc=roc, irv=irv, start=start, end=end)

def datasourceMail(failed_sources, checkTime, testing=False):
  sendMail = SendMail(template_dir="emails/")
  sendMail.formatAndSend(['tung.hoang@gmail.com', 'cuonglv@biendongpoc.vn', 'trungnt@biendongpoc.vn', 'trungtn@biendongpoc.vn'], "datasource", sources=failed_sources, start=checkTime)
