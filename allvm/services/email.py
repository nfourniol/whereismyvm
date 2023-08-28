from email.headerregistry import Address
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from typing import Final
import os
import yaml
from allvm.services.utils import ConfigService

#
# For testing purpose you can use a fake SMTP with: docker run -p 1080:80 -p 25:25 --name maildev maildev/maildev
# https://github.com/maildev/maildev
#
class EmailService:

    def __init__(self):
        cfg = ConfigService()
        self.host = cfg.getSmtpHost()
        self.port = cfg.getSmtpPort()
        self.reply_to = cfg.getMailFrom()
        self.fromAddress = cfg.getMailFrom()
        #self.fromAddress = Address(display_name='Where Is My VM', addr_spec=cfg.getMailFrom())


    def __createEmailMessage(self, to:str, subject:str, body:str):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.fromAddress
        msg['To'] = to
        msg.add_header('reply-to', self.reply_to)
        msg.set_content(body)

        return msg

    def sendEmail(self, to:str, subject:str, body:str):
        msg = self.__createEmailMessage(self, to, body)

        smtp = smtplib.SMTP(self.host, self.port)
        smtp.send_message(msg)
        smtp.quit()
    
    def sendEmailWithAttachment(self, to:str, subject:str, body:str, fileName:str, data:bytes, contentType:str):
        '''msg = self.__createEmailMessage(self, to, body)
        msg.attach(fileName, data, contentType)'''

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.fromAddress
        msg['To'] = to
        msg.add_header('reply-to', self.reply_to)
        msg.attach(MIMEText(body))

        part = MIMEApplication(
            data,
            Name=fileName
        )

        # After the file is closed
        part['Content-Disposition'] = f"attachment; filename={fileName}"
        msg.attach(part)

        smtp = smtplib.SMTP(self.host, self.port)
        smtp.send_message(msg)
        smtp.quit()
