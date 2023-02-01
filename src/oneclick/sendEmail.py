from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from string import Template

from oneclick.discovery.sourceValidation import SourceValidation
from os.path import abspath
from oneclick.config import Config

import smtplib

class EmailNotification(SourceValidation):

    def __init__(cls, config:Config, log_level:int):
        super().__init__(config,cls.__class__.__name__,log_level)
        pass

    def run(cls, config:Config):

        # set up the SMTP server
        s = smtplib.SMTP(host='smtp.office365.com', port=587)
        s.starttls()

        s.login(config.from_email_addrs, config.from_email_passwd)

        # For each contact, send the email:
        for email in list(config.to_email_addrs):
            msg = MIMEMultipart()       # create a message

            # setup the parameters of the message
            msg['From']=config.from_email_addrs
            msg['To']=email
            msg['Subject']=config.email_subject
            message = config.email_body
            # Prints out the message body for our sake
            # print(message)
            cls._log.info(f'sending a mail to {email}')
            # add in the message body
            msg.attach(MIMEText(message, 'plain'))

            discovery_report = abspath(f'{config.report}/{config.project_name}/{config.project_name}-source-code-discovery.docx')
            # attaching docx file
            docx = MIMEApplication(open(discovery_report, 'rb').read())
            docx.add_header('Content-Disposition', 'attachment', filename= f'{config.project_name}-source-code-discovery.docx')
            msg.attach(docx)
            
            # send the message via the server set up earlier.
            s.send_message(msg)
            cls._log.info(f'sent a mail containing discovery report to {email}')
            #del msg
            
        # Terminate the SMTP session and close the connection
        s.quit()
    

