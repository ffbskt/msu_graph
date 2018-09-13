import smtplib
from email.mime.text import MIMEText

class SMTP(object):
    def __init__(self, gmail, password):
        self.gmail = gmail
        self.password = password
        self.raise_server()

    def raise_server(self):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.ehlo()
        self.server.starttls()
        self.server.login(self.gmail, self.password)
        return self.server

    def send(self, to, text):
        msg = MIMEText(text.encode('utf-8'), _charset='utf-8')
        try:
            self.server.sendmail(self.gmail, to, msg.as_string())
        except Exception as e:
            print('SMTP ERROR!', e, to, msg.as_string())

    def close(self):
        self.server.close()
