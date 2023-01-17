from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from string import Template

import smtplib

class EmailNotification:

    def __init__(self) -> None:
        self.MY_ADDRESS = 's.p@castsoftware.com'
        self.PASSWORD = ''

    def get_contacts(self,filename):
        """
        Return two lists names, emails containing names and email addresses
        read from a file specified by filename.
        """
        
        names = []
        emails = []
        with open(filename, mode='r', encoding='utf-8') as contacts_file:
            for a_contact in contacts_file:
                names.append(a_contact.split()[0])
                emails.append(a_contact.split()[1])
        return names, emails

    def read_template(self,filename):
        """
        Returns a Template object comprising the contents of the 
        file specified by filename.
        """
        
        with open(filename, 'r', encoding='utf-8') as template_file:
            template_file_content = template_file.read()
        return Template(template_file_content)

    def send_mail(self):
        names, emails = self.get_contacts('scripts\\mycontacts.txt') # read contacts
        message_template = self.read_template('scripts\\message.txt') # read message template

        # set up the SMTP server
        s = smtplib.SMTP(host='smtp.office365.com', port=587)
        s.starttls()
        s.login(self.MY_ADDRESS, self.PASSWORD)

        # For each contact, send the email:
        for name, email in zip(names, emails):
            msg = MIMEMultipart()       # create a message

            # add in the actual person name to the message template
            message = message_template.substitute(PERSON_NAME=name.title())

            # Prints out the message body for our sake
            # print(message)

            # setup the parameters of the message
            msg['From']=self.MY_ADDRESS
            msg['To']=email
            msg['Subject']="This is TEST"
            
            # add in the message body
            msg.attach(MIMEText(message, 'plain'))

            # attaching png file
            with open('scripts\\example.png', 'rb') as fp:
                img = MIMEImage(fp.read())
                img.add_header('Content-Disposition', 'attachment', filename="example.png")
                msg.attach(img)

            # attaching pdf file 
            pdf = MIMEApplication(open("scripts\\example.pdf", 'rb').read())
            pdf.add_header('Content-Disposition', 'attachment', filename= "example.pdf")
            msg.attach(pdf)

            # attaching docx file
            docx = MIMEApplication(open("scripts\\example.docx", 'rb').read())
            docx.add_header('Content-Disposition', 'attachment', filename= "example.docx")
            msg.attach(docx)
            
            # send the message via the server set up earlier.
            s.send_message(msg)
            #del msg
            
        # Terminate the SMTP session and close the connection
        s.quit()
    

mail_obj=EmailNotification()
mail_obj.send_mail()