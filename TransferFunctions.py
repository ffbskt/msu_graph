import pygsheets
import pandas as pd
import util
import random
import hashlib
import PandasForm, SyncGraph




class AnketeAnswers:
    def __init__(self, key):
        self.pg = pygsheets.authorize(outh_file='other.json')
        self.wks = self.pg.open_by_key(key=key).sheet1
        # df = safe_transfer_to_pd_by_col(wks, [1, 2, 3, 4, 5, 6, 7, 8])

    def safe_load(self, col_list):
        df = self.safe_transfer_to_pd_by_col(self.wks, col_list)
        #print('aa', df.head)
        return df


    def safe_transfer_to_pd_by_col(self, wks, col_list):
         """
             take col one by one and create pd dataframe (more stable then get_as_df)
             col_list = [1, 2, 6...]
         """
         df = pd.DataFrame()
         for col in col_list:

             full_col = wks.get_col(col, include_empty=False)
             # print(col, full_col, full_col[0], len(full_col), df.shape[0])
             diff_coll = df.shape[0] - len(full_col) + 1
             if diff_coll > 0:
                 for i in range(diff_coll):
                     full_col.append('')

             df[full_col[0]] = full_col[1:]
         return df

    def filter_people(self, key_value=('Химфак', '2'), key_column=('Факультет','cource'), ratio="=="):
        """
        :param ratio: operation for compare any of <=. >, ==...
        :param key_value: value for compare with df value in key_col..
        :param key_column: column where we find interesting for us key
        :return: None - inplace update df
        """
        self.df = util.get_row_by_keys(self.df, key_value, key_column, ratio=ratio)

    def score_to_int(self, sc_val):
        return int(sc_val.split('/')[0])

    def mail_hesh(self, mail):
        return hashlib.md5(mail.encode('UTF-8')).hexdigest()

    def get_cource(self, group_number):
        if group_number:
            return str(group_number[0])
        return ''



class Basketball_rules(AnketeAnswers):
    def __init__(self, key, test_norm_points=18):
        super().__init__(key=key)
        self.col_to_rename = {"Номер учебной группы (101, 201, 201э)":'group',
                 "Email Address":'key', # emeil hash
                 "Score":'test_rool', # transform to int
                 'Фамилия и инициалы (Пример: Петров А. Б.)':'suname',
                 "Медицинская группа (на загруженной справке) ":'med'
                }
        self.col_list = [1,2,3,4,5,6,7,8]
        self.cur_col = ['key', 'suname', 'test_rool', 'group', 'med', 'test_points']
        self.test_norm_points = test_norm_points
        # print(self.df.head())#, self.df.columns)

    def add_column_to_df(self, new_col=util.get_dates(5,3,7), cur_col=None):
        """

        :param new_col: add names for new col to df
        :param cur_col: leave omly this columns, when concate with new.
        :return: None - inplace update df
        """
        print('start dates', new_col)
        df2 = pd.DataFrame(
            [[''] * len(new_col)],
            index=self.df.index,
            columns=new_col
        )
        if cur_col is None:
            self.df = pd.concat([self.df, df2], axis=1)
        else:
            self.df = pd.concat([self.df[cur_col], df2], axis=1)

    def update_or_create_from_Rool_Test(self, tittle, folder_id='1OnF9ZpSiO5IYB4Ns15PZgsTc14DVRr3z'):
        fc = PandasForm.SheetCreator(title=tittle, folder_id=folder_id)
        if fc.check_shet_in_folder(pg=self.pg, sheet_name=fc.title):

            # update with insert key
            sg = SyncGraph.Graph(None)
            wks = self.pg.open_by_key(util.search_id_in_list(self.pg.list_ssheets(folder_id), tittle))
            sg.add_key(self.df, wks.sheet1, key_col=['key'])  # .sheet1
            args = {"to_key_colname": ["key", ],
                    "to_values_colname": self.cur_col,
                    }
            util.sync_by_colname(from_wks=self.df, to_wks=wks.sheet1, **args)
        else:
            fc.df = self.df         #[self.col_name]
            fc.create_sheet(pg=self.pg)


    def prepare_df(self):
        self.df = self.safe_load(self.col_list)
        self.df.rename(columns=self.col_to_rename, inplace=True)
        self.df = self.df[self.df.key != '']
        self.df['key'] = self.df['key'].apply(self.mail_hesh)
        self.df['key'] = self.df['key'].apply(str)  # int to long for google docs
        self.df['cource'] = self.df['group'].apply(self.get_cource)
        self.df['test_rool'] = self.df['test_rool'].apply(self.score_to_int)
        self.df['test_points'] = self.df['test_rool'].apply(lambda x: x - self.test_norm_points)

    def get_df(self):
        return self.df


class BasketballBlock():
    pass

class BasketballResults(AnketeAnswers):
    def __init__(self, full_form_key, curent_form_key=None): # form answers #curent_form_key where insert points
        super().__init__(key=full_form_key)
        self.col_to_rename = {"Email Address": 'ref1',
                              "Ещё судьи, почты через пробел": 'ref23',  # emeil hash
                              "Факультет и курс": 'faculty',  # transform to int
                              }


    def add_points(self):
        pass
    
    def get_df(self):
        self.df = self.safe_load(range(1,13)) # 13 - all no empty col
        self.df.rename(columns=self.col_to_rename, inplace=True)
        return self.df 


if __name__ == '__main__':
    #util.read_sheet(name='ch2')
    # Open basketball form and get omly 'cl' columns. change names and df ready to sync.
    cl = [1, 2, 3, 4, 5, 6, 7, 8]
    MIN_TEST_VAL = 10
    br = Basketball_rules('1cWN-sMoaV_5NjWTcjryRx-6uxi29K9KaWt5vHa9vQog')
    br.prepare_df()

    # Get people with propertys and sync with existans
    br.filter_people(('Химфак', '2'))#('Физифак', '2'))#
    br.filter_people(key_value=[MIN_TEST_VAL,], key_column=['test_rool'], ratio=">")
    if 0: #if create new df with dates
        br.add_column_to_df(cur_col=br.cur_col, new_col=util.get_dates(9, 3, 7)) #how much days ago was saturday?
        br.add_
    br.update_or_create_from_Rool_Test('ch2') #ph2



