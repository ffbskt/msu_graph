import time
from SMTP import SMTP
from IMAP import IMAP
from Executor import Executor
from log import write_log
from keys import EmailPassLog


class Requst_processor(object):
    """
    This class have infinite cycle for read, parse and run command, send reply.
    stmp - send mail
    imap - read mail
    executor - make changes in sheet
    """

    def __init__(self, gmail, password, sheets):
        self.smtp = SMTP(gmail, password)
        self.imap = IMAP(gmail, password)
        self.executor = Executor(sheets)

    def run(self):
        period = 0
        while True:
            self.imap.chec_mail()
            # print(self.imap.get_comand())
            for comand in self.imap.get_comand():
                try:
                    print('-', comand)
                    self.executor.execute(comand) # return status and comand
                    #self.executor.transfer() # ?? try &&
                except Exception as e:
                    str_exeption = str(type(e)) + str(e.args)
                    write_log(log=self.reply_on_comand(comand['address'], comand['command'], str_exeption))
                else:
                    write_log(log=self.reply_on_comand(comand['address'], comand['command'], 'SUCCESS'))


            period += 1
            time.sleep(25)

    def reply_on_comand(self, address, command, result):
        self.smtp.send(address, result)
        if result == 'SUCCESS':
            print(result)
        else:
            print('ERROR ', result)
            result = result
        return '/' + address + '/' + command + '/' + result





if __name__ == "__main__":
    r = Requst_processor(EmailPassLog['log'],
                         EmailPassLog['password'],
                         '1MeAYhENafzQMoTKDG-VOLI308ih1wl7SjMLbOkwJU4M'
                         #['174rn-nhlAkbvVF6cI6JMRAfXQGZWxPxi-iNprtHm9fU',]
                         )
    r.run()
