import pygsheets
import pandas as pd
import util
import random
import datetime
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
    
    def add_date(self, dates = util.get_dates(3,3,7)):
        col_name=['key', 'suname', 'test_rool', 'group']
        df2 = pd.DataFrame(
            [[''] * len(dates)], 
            index=self.df.index, 
            columns=dates
        )
        self.df = pd.concat([self.df[col_name], df2], axis=1)
        
            
    
    def score_to_int(self, sc_val):
        if sc_val == "":
            return 0
        return int(sc_val.split('/')[0])

    def mail_hesh(self, mail):
        return hashlib.md5(mail.encode('UTF-8')).hexdigest()

    def get_cource(self, group_number):
        if group_number:
            for letter in str(group_number):
                if letter.isdigit():
                    return str(letter)           
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
    
    def filter_participants(self, key_value=['Физифак', '1'], 
                            key_column=['Факультет','cource']):
        self.filter_people(key_value, key_column)
        self.filter_people([self.test_norm_points], ['test_rool'], ratio=">")
        
        

    def get_df(self):
        return self.df


class BasketballBlock(AnketeAnswers):
    def __init__(self, block_key):
        super().__init__(key=block_key)
        
    def get_test_res(self, ratio='25', col_name="Block1"):
        self.res_df = self.safe_transfer_to_pd_by_col(self.wks, [1,2,3])
        self.res_df["key"] = self.res_df["Email Address"].apply(self.mail_hesh)
        self.res_df["Block1"] = self.res_df["Score"].apply(self.score_to_int)
        self.res_df = util.get_row_by_keys(self.res_df, [ratio,], ['Block1'], ratio=">")
        
    def add_col(self, dest_form_key, col_name="Block1", ind=7):
        self.colname = col_name
        self.dest_wks = self.pg.open_by_key(dest_form_key)
        assert not (self.colname in self.dest_wks.sheet1.get_as_df()), "already have col"
        self.dest_wks.sheet1.insert_cols(ind, values=[self.colname])
        
    def add_results(self, dest_form_key):
        args = {"to_key_colname": ["key",], 
            "to_values_colname": [self.colname],            
           }
        wks = self.pg.open_by_key(dest_form_key)
        util.sync_by_colname(from_wks=self.res_df, to_wks=wks.sheet1, **args)

class BasketballResults(AnketeAnswers):
    def __init__(self, res_form_key, dest_form_key): # form answers #curent_form_key where insert points
        super().__init__(key=res_form_key)
        self.res_form_key = res_form_key
        self.dest_wks = self.pg.open_by_key(dest_form_key)
        self.dest_df = self.dest_wks.sheet1.get_as_df()
        self.todaydate = datetime.datetime.now().strftime("%m-%d")
        self.tomorow = self.dest_df.columns[
            self.dest_df.columns.get_loc(self.todaydate) + 1]
        self.today_col_ind = self.dest_df.columns.get_loc(
            self.todaydate)
        
    def gen_teams(self, numbers=3):
        players_count = sum(
            [int(s or 0) for s in self.dest_df[self.todaydate]])
        if players_count % numbers == 0:
            teams_count = players_count // numbers - 1
        else:
            teams_count = players_count // numbers
        
        team_names = "abcdefghigklmnopq"
        players_count / numbers
        team_list = []
        for i in team_names[:teams_count]:
            team_list.extend(list(i * numbers))
        team_list.extend(list('R' * (players_count % numbers or numbers)))
        random.shuffle(team_list)
        i = 0
        for ind, v in enumerate(self.dest_df[self.todaydate]):
            if v:
                self.dest_df[self.tomorow][ind] = team_list[i]
                i += 1
        self.dest_wks.sheet1.update_col(
            index=self.today_col_ind + 2,
            row_offset=1,values=self.dest_df[self.tomorow].values.tolist())
        
    def add_results_points(self, fac_id):
        self.res_df = self.wks.get_as_df()
        for ind, line in self.res_df.iterrows():
            if not line['counted'] and fac_id[line['Faculty']]:
                print(ind)
                self.wks.update_cell((ind + 2, self.res_df.columns.get_loc('counted') + 1), val=1)
                self.dest_wks = self.pg.open_by_key(fac_id[line['Faculty']])
                df = self.dest_wks.sheet1.get_as_df()
                for col in range(5,9):
                    if line[col] != '':
                        for ind, t_key in enumerate(line[col]):
                            #print(t_key, line['Faculty'])
                            fv = round(0.1 *(4.3 - ind) ** 1.4, 2) + 0.001 * 0.1 ** ind
                            self.add_to_colA_if_colB(df, 
                                                colA=self.todaydate, 
                                                colB=self.tomorow, 
                                                cond=t_key, val=fv)
                            #print(line['Faculty'], t_key, fv)
                #print('k', df[['suname', self.todaydate]][:8])
                #add remove teams ? ? 
                self.dest_wks.sheet1.update_col(index=self.today_col_ind + 1,
                                                row_offset=1,
                                                values=df[self.todaydate].values.tolist())
                
    def add_to_colA_if_colB(self, df, colA, colB, cond='a', val=0.3):
        df.loc[df[df[colB] == cond].index, colA] += val
    
    

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



