import pygsheets
import util
from GDrive import GDrive


class Executor(object):
    def __init__(self, sheet_id):
        self.pg = pygsheets.authorize(outh_file='other.json')
        self.graph_wks = util.read_sheet(key=sheet_id, pygsheet=self.pg)
        self.graph_df = self.graph_wks.get_as_df()
        self.drive = None # GDrive()

    def execute(self, comand):
        """ Change value in doc_name shete row contain email
        (comand['address']) in column named sell_name

        :param comand: {'address': email, 'command': 'cell_name doc_name/value'}
        :return: Error if can't find or OK
        """
        subject_split = comand['command'].split()
        if subject_split[0] == 'RE:':
            subject_split = subject_split[1:]
        assert len(subject_split) == 2, ('Wrong command format exc')
        # print('ex:', comand)
        request, value = subject_split
        request = self.correct_request(request)
        if request == "Синк":
            pass
        elif request == 'Перевод':
            """ 
            You need main_wks with all group(postfix of value), new_wks (value), old_wks (read in main_wks)
            check email then use suname and group like key
            """
            node, link = util.affilation_wks(util.get_postfix(value), graph_df=self.graph_df)

            # TODO check_value in wks or ...
            # TODO if drive already init on correct sheet_id
            self.drive = GDrive(sheet_id=node, graph=self.graph_df)
            self.drive.transfer(id=comand['address'], new_group=value,
                                key_column=['Почта'], value_column='Секция')
        else:
            # change value. requst any column where value should change
            node, link = util.affilation_wks(util.get_postfix(value), graph_df=self.graph_df)
            # TODO if drive already init on correct sheet_id
            self.drive = GDrive(sheet_id=node, graph=self.graph_df)
            self.drive.change_cell_with_id(key_column=['Почта'], id=comand['address'],
                                           value_column=request, value=value)




    def correct_request(self, req):
        """ Lock for change only what student may change

        :param req:
        :return: Exception or else..
        """
        if not (util.space_cut(req.lower()) in ['перевод', 'синк', 'группа', 'справка']):
            raise Exception('Error', 'wrong request:' + req +
                        ' first world must be "Перевод" or "Синк"')
        if util.space_cut(req.lower()) == 'перевод':
            return 'Перевод'
        else:
            return "Синк"

    def is_correct_value(self, df, value):
        assert util.space_cut(value) in list(df['Секция'].unique()), Exception('Error', 'wrong subject: ' + value)



if __name__ == "__main__":
    sheets = '19FRWh10ZAkM0vX620Clq9UOPJD1M90WccgJWKqov5Kk'
    #sheets = ['174rn-nhlAkbvVF6cI6JMRAfXQGZWxPxi-iNprtHm9fU'] # work
    sheets = '1MeAYhENafzQMoTKDG-VOLI308ih1wl7SjMLbOkwJU4M'

    #pargs = {'col':5}
    #function_command_correspondence = {'перевод': [change_cell, pargs],
    #                                   'группа':1}
    e = Executor(sheets)


    #pg = pygsheets.authorize(outh_file='other.json')   #Волейбол_Волконская_Г_Н_ФФ1 Баскетбол_Волконский_Д_А_ФФ1
    comand = {'address': 'ffbskt@gmail.com', 'command': 'Перевод ОФП_Киртоакэ_А_М_ФФ1'}
    
    print (e.execute(comand))
    #print (e.transfer())
    #print(e.correct_value(e.wkses[0], 'Волейбол_Волконская_Г_Н', 'Перевод'))
    
