import imaplib
import re
import email
from bs4 import UnicodeDammit
from keys import EmailPassLog

class IMAP(object):
    def __init__(self, gmail, password):
        self.imap_host = 'imap.gmail.com'
        self.gmail = gmail
        self.password = password
        self.raise_imap()
        self.unseem_mesages = []

    def raise_imap(self):
        self.imap = imaplib.IMAP4_SSL(self.imap_host)
        self.imap.login(self.gmail, self.password)

    def chec_mail(self):
        self.unseem_mesages = []
        self.imap.select('Inbox')
        typ, all_data = self.imap.search(None, 'UnSeen')
        for num in all_data[0].split():
            typ, data = self.imap.fetch(num, '(RFC822)')
            self.unseem_mesages.append(data)
            self.imap.store(num, '+FLAGS', '\Seen')
        return self.unseem_mesages

    def get_comand(self):
        self.comands = []
        for message in self.unseem_mesages:
            comand = self.message_to_requst(message[0])
            self.comands.append(comand)
        return self.comands

    def message_to_requst(self, mes):
        message = email.message_from_bytes(mes[1])
        from_adress = re.findall(r"\<.+>", message['From']) or ['<' + message['From'] + '>']
        dammit = UnicodeDammit(email.header.decode_header(message['Subject'])[0][0])
        subject = dammit.unicode_markup
        request = {'faculty': None, 'address': from_adress[0][1:-1], 'command': subject}
        return request



if __name__ == '__main__':
    im = IMAP(EmailPassLog['log'], EmailPassLog['password'])
    print('email read: ', im.chec_mail())
    print('comands: ', im.get_comand())


