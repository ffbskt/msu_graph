import pygsheets
import util
import PandasForm
import itertools
import time


class GDrive:
    def __init__(self, sheet_id: str, graph=None, pg_outh_pass='other.json'):
        """

        :param sheet_id: id where we will do change
        :param graph: sheet with pair <name of sheet, id> to open and edit relation sheets
        """
        self.sheet_id = sheet_id
        self.pg = pygsheets.authorize(outh_file=pg_outh_pass)
        self.wks = util.read_sheet(key=sheet_id, pygsheet=self.pg)
        self.df = self.wks.get_as_df()
        if isinstance(graph, str):
            self.graph_df = util.read_sheet(key=graph, pygsheet=self.pg).get_as_df()
            self.graph_id = graph
        elif graph is not None:
            self.graph_df = graph
            self.graph_id = None
        elif graph is None:
            pass  # TODO create graph

    def downloads_images(self, drive_http, folder_pass):
        pass



    def find(self, key_column, id, value_column):
        row = util.get_row_by_keys(self.df, key_value=id, key_column=key_column)
        #print('--', row)
        return row[value_column] #row_ind + 2, col_ind + 1 # in wks from 0 + head

    def change_cell(self, row, col, val):
        self.wks.update_cell((row, col), val)

    def change_cell_with_id(self, key_column, id, value_column, value):
        cur_value = self.find(key_column, id, value_column)
        col = self.df.columns.get_loc(cur_value.columns[0])
        row = cur_value.index[0]
        print(row, col)
        self.change_cell(row+2, col+1, value)


    def transfer(self, id, new_group, key_column=None, value_column="Секция"):
        main_df = self.wks.get_as_df()
        main_row = util.get_row_by_keys(main_df, key_value=[id], key_column=key_column)
        old_wks_name = main_row[value_column].values[0]
        old_wks = util.read_sheet(util.affilation_wks(old_wks_name,
                                            self.graph_df
                                            )[0]
                             )
        new_wks = util.read_sheet(util.affilation_wks(new_group,
                                            self.graph_df
                                            )[0]
                             )
        old_row = util.get_row_by_keys(old_wks.get_as_df(),
                                  main_row[['ФИО', 'Группа']].values[0],
                                  ['ФИО', 'Группа'])
        old_wks.delete_rows(int(old_row.index[0] + 2))
        util.add_row_down(wks=new_wks, values=list(old_row.values[0]))
        col = main_df.columns.get_loc(value_column) + 1
        self.change_cell(col=col, row=main_row.index[0]+2, val=new_group)
        #change cell main_wks

    def generate_from_main(self, category=[], key=[]):


        fc = PandasForm.SheetCreator()



    def generate(self, category=[], keys=[], current_folder=None, graph_wks=None):
        """
                Take main df and create own wks to each category(or group) in same drive folder
                put it to graph with backlink to main (# TODO add separete link??)
                :param main_wks:
                :param category:
                :param key:
                :return:
        """
        all_requsts_args = []
        for name in category:
            all_requsts_args.append(self.df[name].unique())
        requst = util.create_requst(category)
        generated_ids = {}

        for requst_arg in itertools.product(*all_requsts_args):
            filter_df = self.df.query(requst.format(*requst_arg))
            if not filter_df.empty:
                #print('Main , Open list', str(requst_arg), category, keys, "Extra point")
                #print(str(requst_arg), 'Main , Open list', 'Exams')
                #print(str(requst_arg))

                ##graph_wks.insert_rows(1, number=1, values=[1,2,3], inherit=False)
                #title = '_'.join([str(arg) for arg in requst_arg])
                title = requst_arg[0]
                fc = PandasForm.SheetCreator(title=title, folder_id=current_folder)
                fc.create_from_standart(dates=util.get_dates(2, 3, 7))
                #print(filter_df[keys], filter_df[keys].values)
                fc.add_objects(key_col=keys, key_val=filter_df[keys].values)
                # print(fc.df)
                wks = fc.create_sheet(self.pg)
                util.edit_col_lenth(wks)
                generated_ids[wks.spreadsheet.title] = wks.spreadsheet.id

        self.create_graph_line(node_short_name=self.wks.spreadsheet.title,
                               node_dict={self.wks.spreadsheet.title: self.wks.spreadsheet.id},
                               links_dict=generated_ids,
                               args='{"to_key_colname": ["ФИО", "Группа"], "to_values_colname": ["внешнии_баллы"]}'
                               )
        self.create_graph_line(node_short_name=self.wks.spreadsheet.title,
                               node_dict=generated_ids,
                               links_dict={
                                   self.wks.spreadsheet.title: self.wks.spreadsheet.id},
                               args='{"to_key_colname": ["ФИО", "Группа"], "to_values_colname": ["посещения"]}'
                               )
        return generated_ids


    def create_graph_line(self, Pass=1, node_short_name='', node_dict={},
                          last_sink_time=time.time(),
                          parse_funktion='',
                          links_dict={},
                          straight_link_col='',
                          args='{"to_key_colname": "ФИО", "to_values_colname": []}',
                          convert_function='',
                          can_add_key='',
                          graph_id=None
                          ):
        graph_wks = util.read_sheet(key=(graph_id or self.graph_id))
        link_names, links = self.dict_to_title_and_link(links_dict)
        node_names, nodes = self.dict_to_title_and_link(node_dict)


        row_values = [Pass, node_short_name,node_names, nodes, last_sink_time, parse_funktion, link_names, links,
                      straight_link_col, args, convert_function, can_add_key
                      ]
        graph_wks.insert_rows(1, number=1, values=row_values, inherit=False)
        pass

    def dict_to_title_and_link(self, dict_t_l):
        link_names = ''
        links = ''
        for name, link_id in dict_t_l.items():
            link_names += name + ' '
            links += self.create_link_from_id(link_id) + ' '
        return link_names, links


    def create_link_from_id(self, id):
        return 'https://docs.google.com/spreadsheets/d/' + str(id)



    def create_protected_range(self, sheet_id, end_range, editors_mails, start_range=[0, 0]):
        gridrange = {
            "sheetId": 0,
            "startRowIndex": start_range[0],
            "endRowIndex": end_range[0],
            "startColumnIndex": start_range[1],
            "endColumnIndex": end_range[1],
        }
        editors = {
            "users": editors_mails,
            "groups": [
            ],
            "domainUsersCanEdit": True,
        }
        request = {"addProtectedRange": {
            "protectedRange": {
                "range": gridrange,
                "editors": editors
            },
        }}
        print(11)
        sheet_id = sheet_id or self.sheet_id
        self.pg.sh_batch_update(sheet_id, request, None, False)


    def edit_all_forms_in_graph_sell(self, graph_c_name, graph_r):
        for link in self.graph_df[graph_c_name][graph_r].split():
            #print(link)
            sheet_id = util.get_sheet_id_from_link(link)
            #print(sheet_id)
            self.create_protected_range(sheet_id, end_range=[50,5], editors_mails=['ffbskt@gmail.com'])




if __name__ == "__main__":
    if 0:
        g = GDrive('1htiRE_TSayRYGu4FDwTua_X9oOWM5LfCfo1a5G-khxU')
        cur_value = g.find(key_column=['ФИО'], id=['Лукманов А Р'], value_column=['03-03'])
        print(cur_value, type(cur_value))
        # print(cur_value.index[0],)
        g.change_cell_with_id(key_column=['ФИО'], id=['Лукманов А Р'], value_column=['03-10'], value='23')

    if 0:
        main_sheet = GDrive(sheet_id='174rn-nhlAkbvVF6cI6JMRAfXQGZWxPxi-iNprtHm9fU',
                            graph='1MeAYhENafzQMoTKDG-VOLI308ih1wl7SjMLbOkwJU4M')
        #main_sheet.transfer(id='ffbskt@gmail.com', new_group='Футбол_Белоглазов_В_В_ФФ1',
        #                    key_column=['Почта'], value_column='Секция')

        df = util.read_sheet(name='Футбол_Белоглазов_В_В_ФФ1').get_as_df()
        print(main_sheet.find(key_column=['Почта'], id=['ffbskt@gmail.com'], value_column='Секция'))
        print('Тест Т Т' in df['ФИО'].values)

    #g = GDrive('1tV9pzE0Ds8-eW5btij6Wvn-c3xljBeTQ0ASh9cX-Kk4',
    #           graph='1ZR38L8tFMdUTODVQ0cdz79jPKX4xpNn7R11S82u5Jyk')
    #g.edit_all_forms_in_graph_sell('link', 1)
    #g.create_protected_range(end_range=[50,5], editors_mails=['ffbskt@gmail.com'])
    #g.edit_col_lenth()
    #print(g.wks.get_values(start=(1,1), end=(3,5), value_render='FORMULA'))

    # GENERATE SUBSET
    # put main wks
    if 0:
        g = GDrive(sheet_id='1QaeRcyKi92a_Z6g4koYnfQB0nBtXBBvpkEsACtrKSn0',
                   graph='1ZR38L8tFMdUTODVQ0cdz79jPKX4xpNn7R11S82u5Jyk'
                   )
        g.generate(category=['Секция', 'Факультет'], keys=['ФИО', 'Группа'],
                   current_folder='19PZiIxtt9nvLDHst4EZp-FMWYQO4yrKa',
                   graph_wks=util.read_sheet('1ZR38L8tFMdUTODVQ0cdz79jPKX4xpNn7R11S82u5Jyk'))
    #wks = util.read_sheet('1QaeRcyKi92a_Z6g4koYnfQB0nBtXBBvpkEsACtrKSn0')
    #print(wks.spreadsheet.id.spreadsheet.id)



    #g = GDrive(sheet_id='1cWN-sMoaV_5NjWTcjryRx-6uxi29K9KaWt5vHa9vQog',
    #           graph='1at8ivfcSDq3W_LFdwzFqVuYfQ27c18Ka-F1Cpen844g'
    #           )
    
    g = GDrive(sheet_id='1pWKKo-zDPeKzt9aNdGAx3qh5zMFkqE7D2r6Fr8z_tLM',
               graph='1led4JXV6IWNxmvYKsXaV_CCsQkAHsIyPqBgDvkrj0kE')
    g.generate(category=["В какой учебной группе вы хотели  бы посещать занятия по физической культуре"], keys=["Фамилия", "Имя", "Отчество"],
                   current_folder='1IKEAsUHu_BjWu2fX3g3yyt89u7QAU5Cs',)
                   #graph_wks=util.read_sheet('1ZR38L8tFMdUTODVQ0cdz79jPKX4xpNn7R11S82u5Jyk'))