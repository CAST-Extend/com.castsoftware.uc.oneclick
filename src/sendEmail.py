import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
send_from = 'nevinkap@gmail.com'
send_to = 'n.kaplan@castsoftware.com'
password = 'wjcboahhwqpyitbc'

msg = MIMEMultipart()   
msg['From'] ='nevinkap@gmail.com'
msg['To'] = 'n.kaplan@castsoftware.com'
msg['From'] =send_from = 'nevinkap@gmail.com'
msg['Date'] = formatdate(localtime=True)
msg['Subject'] = 'This is a test email'

with smtplib.SMTP_SSL(smtp_server, port) as s:
    s.ehlo()
    s.login(send_from, password)
    s.sendmail(send_from, send_to, msg.as_string())



