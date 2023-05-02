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

environment = Environment(loader=FileSystemLoader("emails/"))

def sendmail(to, subject, content):
  port = 587  # For SSL
  smtp_server = "smtp.office365.com"
  password = "bdpoc@2602"

  # Create a secure SSL context
  context = ssl.create_default_context()
  email = "pdmone@biendongpoc.vn"
  with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(email, password)
    msg = MIMEText(content)
    msg["Subject"] = subject
    msg["From"] = email
    msg["To"] = ",".join(to) if type(to) == list else to
    server.sendmail(email, to, msg.as_string())

def urgentMail(urgents, start, end, testing=False):
  if testing:
    formatAndSend(['tung.hoang@gmail.com', 'cuonglv@biendongpoc.vn', 'trungnt@biendongpoc.vn', 'hiennv@biendongpoc.vn'], 'urgent', events=urgents, start=start, end=end)
  else:
    formatAndSend([RES, REE], 'urgent', events=urgents, start=start, end=end)

def wetGasSealMail(seals, start, end, testing=False):
  if testing:
    formatAndSend([
      'tung.hoang@gmail.com', 
      'cuonglv@biendongpoc.vn', 
      'trungnt@biendongpoc.vn', 
      'hiennv@biendongpoc.vn'
    ], 'wetseals', seals=seals, start=start, end=end)
  else:
    formatAndSend([RES, REE, EnI_SUPV, ASSISTANT_EnI_SUPV], 'wetseals', seals=seals, start=start, end=end)

def formatAndSend1(to, templateName, urgents, start, end):
  subject_template = environment.get_template( f"{templateName}.subject.tpl" )
  subject = subject_template.render()

  content_template = environment.get_template( f"{templateName}.tpl" )
  content = content_template.render(events=urgents, start=start, end=end)
  print(content)
  sendmail(to, subject, content)

def formatAndSend(to, templateName, **kwargs):
  subject_template = environment.get_template( f"{templateName}.subject.tpl" )
  subject = subject_template.render()

  content_template = environment.get_template( f"{templateName}.tpl" )
  content = content_template.render(**kwargs)
  sendmail(to, subject, content)

def criticalMail(criticals, start, end, testing=False):
  if testing:
    formatAndSend(['tung.hoang@gmail.com', 'cuonglv@biendongpoc.vn', 'trungnt@biendongpoc.vn', 'hiennv@biendongpoc.vn'], 'critical', events=criticals, start=start, end=end)
  else:
    formatAndSend([RES, REE, CRE, FIELD_SUPV, TL_RES], 'critical', events=criticals, start=start, end=end)

def transientMail(action, start, end, testing=False):
  if testting:
    formatAndSend(['tung.hoang@gmail.com', 'cuonglv@biendongpoc.vn', 'trungnt@biendongpoc.vn', 'hiennv@biendongpoc.vn'], 'transient', action=action, start=start, end=end)
  else:
    formatAndSend([RES, REE], 'transient', action=action, start=start, end=end)

def dailyMail(nan=[], overange=[], roc=[], irv=[], start=None, end=None):
  formatAndSend([RES, REE, EnI_SUPV, ASSISTANT_EnI_SUPV], 'daily', nan=nan, overange=overange, roc=roc, irv=irv, start=start, end=end)

def testDailyMail(nan=[], overange=[], roc=[], irv=[], start=None, end=None):
  #formatAndSend([RES, REE, EnI_SUPV, ASSISTANT_EnI_SUPV], 'daily', nan=nan, overange=overange, roc=roc, irv=irv, start=start, end=end)
  formatAndSend(['tung.hoang@gmail.com', 'cuonglv@biendongpoc.vn', 'trungnt@biendongpoc.vn', 'hiennv@biendongpoc.vn'], 'daily', nan=nan, overange=overange, roc=roc, irv=irv, start=start, end=end)

