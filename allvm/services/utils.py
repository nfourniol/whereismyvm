from typing import Final
import os
import yaml

class ConfigService:

    BASE_DIR: Final=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../..")
    )

    def __init__(self):
        # Load configuration file that contains data about ESXi connections
        self.config = None
        with open(os.path.join(ConfigService.BASE_DIR, 'config.yaml'), 'r') as file:
            self.config = yaml.full_load(file)

    def getMailRecipients(self):
        return self.config.get('mail_recipients')
    
    def getMailFrom(self):
        return self.config.get('mail_from')
    
    def getSmtpHost(self):
        return self.config.get('smtp_host')
    
    def getSmtpPort(self):
        return self.config.get('smtp_port')
