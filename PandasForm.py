import util
import pandas as pd
import re
import pygsheets
import hashlib
import datetime

class SheetCreator: # refactor! its sheet creator
    """
    Pandas Form with init
    Try to solve problem with add formula
    Now call add_objects and object come with default formula (what of protected range?/)
    """
    def __init__(self, title: object, header: object = None, formulas: object = None, folder_id: object = None) -> object:
        
        self.title = title
        self.header = header  # - top row in sheet
        self.formulas = formulas
        self.folder_id = folder_id
        self.df = pd.DataFrame(columns=header)
        
    def check_shet_in_folder(self, pg, sheet_name):
        # TODO shet -> sheet title ->tittle
        for exist in pg.list_ssheets(parent_id=self.folder_id):
            if exist['name'] == sheet_name:
                return True
        return False

    def sync_update_sheet(self, pg):
        """
        find same key and apdate values or add new key
        :param pg:
        :return:
        """
        # TODO open by key
        wks = pg.open(self.title)




    def create_or_update(self, pg):
        if self.check_in_folder(self.title):
            return self.update_sheet(pg)
        else:
            return self.create_sheet(pg)

    def create_sheet(self, pg):
        # TODO to GDrive
        #if c.list_ssheets(parent_id=self.folder_id)
        sh = pg.create(title=self.title, parent_id=self.folder_id)
        sh.sheet1.set_dataframe(df=self.df, start='A1')
        return sh.sheet1

    def update_sheet(self, wks):
        # TODO to GDrive
        wks.set_dataframe(df=self.df, start='A1')

    def init_from(self, wks_df):
        self.df = wks_df
        self.header = self.df.columns

    def load_from_template(self):
        """
        Init from frame contain header, formulas..
        :param wks_df:
        :return:
        """
        pass

    def create_df(self, header=None): #&&???????
        self.header = header
        self.df = pd.DataFrame(columns=header)

    def add_objects(self, key_col, key_val):
        """
        Paste value and default formulas
        :param key_col: [1,2,3]
        :param key_val: [[1,2,3]]
        :return:
        """
        last_row = self.df.shape[0]
        for i, val in enumerate(key_val):
            formula = self.put_ind_to_formuls(self.formulas.copy(), i + last_row + 2)
            new_row = pd.DataFrame(data=[formula], columns=self.header)
            new_row[key_col] = val
            self.df = self.df.append(new_row)
        #print(self.df)

    def put_ind_to_formuls(self, formulas, ind):
        for i, val in enumerate(formulas):
            if '=' in val and val[0] == '=':
                number_bracets = len(re.findall('\{\}', val))
                formulas[i] = val.format(*([ind] * number_bracets))
        return formulas

    def create_from_standart(self, dates=util.get_dates(0, 3, 7)):
        stl = StandartFormLibrary(dates)
        self.header = stl.header1
        self.formulas = stl.formulas

    #def add_multiple_value(self, key_columns, key_values):
    #    for key_val in key_values:
    #        self.add_objects(key_col=key_columns, key_val=key_val)

class StandartFormLibrary:
    def __init__(self, dates):
        """

        :param dates: util.get_dates(2,3,7) create list of week dates
        """
        self.header1 = ['ФИО',
                  'Группа',
                  'Проц_посещений_от_лучшего',
                  'посещения',
                  'ВСЕГО',
                  'внешнии_баллы',
                  'доп_баллы',
                  'Зачет'
                  ]
        self.header1.extend(dates)
        self.formulas = ['','','=ROUND(D{}/MAX(D2:D101) * 100)', '=SUM(H{}:ZZ{})', '=D{}*3+F{}+G{}','','']
        self.formulas.extend([''] * (len(self.header1) - len(self.formulas)))

def open_protected_today(key, pg):
    
    wks = util.read_sheet(key)
    df = wks.get_as_df()
    col = datetime.datetime.now().strftime("%m-%d")
    ind = df.columns.get_loc(col)
    
    #delete protected range
    request = {
              "deleteProtectedRange": {
                "protectedRangeId": 1,
              }
            }
    try:
        pg.sh_batch_update(key, request, None, False)
    except:
        pass
    #set new range
    gridrange = {
      "sheetId": 0,
      "startRowIndex": 0,
      "endRowIndex": 50,
      "startColumnIndex": 0,
      "endColumnIndex": ind,
    }
    editors = {
      "users": [
        "ffbskt@gmail.com",
      ]      
    }
    request = {"addProtectedRange": {
                "protectedRange": {
                "protectedRangeId": 1,
                "range": gridrange,
                "editors": editors
            },

        }}
    pg.sh_batch_update(key, request, None, False)


if __name__ == "__main__":

    d = util.get_dates(2,3,7)
    stl = StandartFormLibrary(d)
    #for i, val in enumerate(stl.formulas):
    #   if '=' in val and val[0] == '=':
    #        number_bracets = len(re.findall('\{\}', val))
    #        stl.formulas[i] = val.format(*([2] * number_bracets))
    #        #print(val.format(2))
    #print(stl.formulas)

    ##################
    gf = SheetCreator('t1', header=stl.header1, formulas=stl.formulas, folder_id='1ncBfOFctKPVRKBYwrc58U5_UaD-d0D30')

    gf.add_objects(key_col=['ФИО', 'Группа'], key_val=[['art', 109], ['ben', 103]])
    pg = pygsheets.authorize(outh_file='other.json')
    gf.create_sheet(pg)