import pygsheets
import pandas as pd
#from keys import GoogleDrivePermision
import re
from datetime import datetime, timedelta
import numpy as np


def read_sheet(key=None, name=None, pygsheet=pygsheets.authorize(outh_file="/GoogleDrivePermision.json")):
    assert not (key is None and name is None), 'Add key or name'
    if name is None:
        sheet = pygsheet.open_by_key(key)
    if key is None:
        sheet = pygsheet.open(name)
    return sheet.sheet1

def search_id_in_list(list_sheets, name):
    """
       find id with name in list_sheet=c.list_ssheets(folder_id)
    """
    for sheet in list_sheets:
        if sheet['name'] == name:
            return sheet['id']
    return None


def safe_transfer_to_pd_by_col(wks, col_list):
    """
        take col one by one and create pd dataframe (more stable then get_as_df)
        col_list = [1, 2, 6...]
    """ 
    df = pd.DataFrame()
    for col in col_list:
        
        full_col = wks.get_col(col, include_empty=False)
        #print(col, full_col, full_col[0], len(full_col), df.shape[0])
        diff_coll = df.shape[0] - len(full_col) + 1
        if diff_coll > 0: 
            for i in range(diff_coll):
                full_col.append('')
            
        df[full_col[0]] = full_col[1:]
    return df

def search_id_in_list(list_sheets, name):
    for sheet in list_sheets:
        if sheet['name'] == name:
            return sheet['id']
    return None

def copy(df, key_col=[0], key_row=None, values_col=[]):
    # key_col = [1,2,6]
    assert (key_col != []), 'Empty key column'
    if key_row is None:
        key_row = range(0, df.shape[0])
    #print (key_row, key_col)
    #key_col.extend(values_col)
    ids_range = df.iloc[key_row, key_col]
    value_df = df.iloc[key_row, values_col]
    return ids_range, value_df

def join_colums_values(df, crange=[], rrange=None, remove=True):
    new_df = df.copy()
    if rrange is None:
        rrange = [0, new_df.shape[0]]
    for ind, line in enumerate(new_df.iloc[rrange[0]:rrange[1], crange[0]:crange[1]].iterrows()):
        #print ind, list(line[1]), 'ee', ' '.join(line)
        new_df.iloc[[rrange[0] + ind], [crange[0]]] = ' '.join(list(line[1]))
    #if remove:
    #    return new_df.drop(range(crange[0] + 1,crange[1]), axis=1)
    return new_df


def join_suname_to_init(df, crange=[], rrange=None, remove=True):
    # 3 to 1
    new_df = df.copy()
    rrange = [0, new_df.shape[0]]
    for ind, line in enumerate(new_df.iloc[rrange[0]:rrange[1], crange[0]:crange[1]].iterrows()):
        #print (ind, list(line[1]), 'ee')#, ' '.join(line))
        listname = list(line[1])
        try:
            init = listname[0] + ' ' + listname[1][0]
            if len(listname) == 3 and listname[2] is not None and listname[2]!='':
                #print(listname)
                init += ' ' + listname[2][0]
        except Exception as e:
            print(e)
            continue
        new_df.iloc[[rrange[0] + ind], [crange[0]]] = init
    #print (init, new_df.head())
    #if remove:
    #    return new_df.drop(range(crange[0] + 1,crange[1]), axis=1)
    return new_df

#################################################################
##### Sync
########################################################################


def paste(df, past_indexs=[], values_crange=1, past_values=[], sub=True):
    """

    :param df:
    :param past_indexs:
    :param values_crange:
    :param past_values:
    :param sub: if True and any value already exist - just pass
    :return:
    """
    #print('aa', past_indexs)
    number_of_pasted = 0
    #print ( past_values)
    for ind in past_indexs:
        if ind[1] == []:
            continue
        if len(ind[1]) == 1:
            cur_value = df.iloc[ind[1][0], values_crange]
            #print('ss', not sub, cur_value.values[0],cur_value.values.all()=='','ss')
            if not sub and any(v != '' for v in cur_value.values[0]):
                continue
                # error_message = 'already has value {} add sub=True to sub'.format(df.iloc[ind[1][0], values_crange])
                # raise BaseException(error_message)
            #print(ind[1][0], past_values[ind[0]], values_crange)

            if len(values_crange) == 1:
                df.iloc[ind[1][0], values_crange] = past_values[ind[0]][0]
            else:
                df.iloc[ind[1][0], values_crange] = past_values[ind[0]]
            number_of_pasted += 1
    print('number_of_pasted: ',number_of_pasted)

def line_find_index(df, words=[], row='head'):
    col_indexes = []
    if row == 'head':
        for word in words:
            col_indexes.append(df.columns.get_loc(word))
    else:
        # write if need
        pass
    return col_indexes

def get_ind(df, colname, ifval):
    """
    Change True/False list to index list where index mean df[col] == ifval
    :param df:
    :param colname:
    :param ifval:
    :return:
    """
    return [str(i[1]) for i in zip(df[colname] == ifval, df.index) if i[0]]

def find_indexs(to_ids, from_ids):
    if to_ids.shape >= from_ids.shape:
        return get_indexs(to_ids, from_ids)
    else:
        return convert_indexs(get_indexs(from_ids, to_ids))

def convert_indexs(indexs):
    new_indexs = []
    for ind in indexs:
        if not ind[1].empty:
            new_indexs.append((ind[1][0], [ind[0]]))
    return new_indexs

def get_indexs(to_ids, from_ids=[]):
    indexs = [] # id ind -> df ind
    for i, from_id in enumerate(from_ids.iterrows()):
        # print('asd',i, from_id, type(from_id))
        _, row = from_id
        #print(row.values, from_ids.columns)
        index = get_row_by_keys(to_ids, key_column=list(from_ids.columns), key_value=row.values).index
        #print(index)
        if index == []:
            print (i, 'Can"t find: ', from_id)
        if len(index) > 1:
            print ('More than one find: ', from_id)
        #print('sfd', i, index)
        indexs.append((i, index))
    return indexs


def sync(from_wks, to_wks, from_key_col, from_values_col, to_key_col, to_values_col, sub=True):
    if isinstance(from_wks, pygsheets.worksheet.Worksheet):
        from_df = from_wks.get_as_df()
    else:
        from_df = from_wks
    to_df = to_wks.get_as_df()
    from_values = from_df.iloc[:, from_values_col]
    indexes = find_indexs(to_ids=to_df.iloc[:, to_key_col],
                          from_ids=from_df.iloc[:, from_key_col]
                          )
    paste(df=to_df,
          past_indexs=indexes,
          values_crange=to_values_col,
          past_values=from_values.values.tolist(),
          sub=sub
          )

    for i, col in enumerate(to_values_col):
        # print('upd ->',col, to_df.iloc[:,to_values_col[i]].values.tolist())
        to_wks.update_col(col + 1,
                          to_df.iloc[:, to_values_col[i]].values.tolist(),
                          row_offset=1
                          )

    return to_df  # , to_values_col

def sync_by_colname(from_wks, to_wks, to_key_colname, to_values_colname,
                    from_key_colname=None, from_key_row=None, from_values_colname=None,
                    sub=True
                   ):
    if isinstance(from_wks, pygsheets.worksheet.Worksheet):
        from_df = from_wks.get_as_df()
    else:
        from_df = from_wks
    # support only for one column for key or value
    to_df = to_wks.get_as_df()
    to_key_col = list(map(to_df.columns.get_loc, to_key_colname))
    to_values_col = list(map(to_df.columns.get_loc, to_values_colname)) #line_find_index(to_df, words=to_values_colname) # --//--
    from_key_colname = from_key_colname or to_key_colname
    from_values_colname = from_values_colname or to_values_colname
    from_key_col = list(map(from_df.columns.get_loc, from_key_colname))
    from_values_col = list(map(from_df.columns.get_loc, from_values_colname))
    #print(from_key_col, from_values_col, to_key_col, to_values_col)
    return sync(to_wks=to_wks,
                from_wks=from_df,
                from_key_col=from_key_col,
                from_values_col=from_values_col,
                to_key_col=to_key_col,
                to_values_col=to_values_col,
                sub=sub
               )


###### Transfer ######
def create_requst(col_name, ratio='==', logic='&'):
    # "{}" - !format if here int [2,3] if str ['"abs"', '"dfs"']
    requst = ''
    for name in col_name:
        requst += name + ratio + '{}' + logic
    return requst[:-1]

def fill_sheet(wks, df):
    array = []
    array.append(list(df))
    for line in df.as_matrix():
        #print(list(line))
        array.append(list(line))
    wks.update_cells('A1', values=array)

def make_new_df(filter_df, new_head):
    same_colmn = [name for name in list(filter_df) if name in new_head]
    new_df = pd.DataFrame(columns=new_head)
    #other_colmn = [name for name in new_head if not (name in list(filter_df))]
    new_df[same_colmn] = filter_df[same_colmn]
    new_df = new_df.fillna('')
    return new_df

#def open_by_main(main_df, col_name, key_col, key_val): #no usage -> get row by keys
#    requst = create_requst(key_col)
#    adress = main_df.query(requst.format(*key_val))[col_name]
#    print ('--->', adress.values[0], '--')#, '_'.join(adress.values[0])) # ???
#    return '_'.join(adress.values[0])

def edit_col_lenth(wks, col_length=None, last_col_length=40):
    if col_length is None:
        col_length = [250,60]
    for ind, length in enumerate(col_length):
        wks.adjust_column_width(start=ind, pixel_size=length)
    wks.adjust_column_width(start=ind, end=wks.cols, pixel_size=last_col_length)

def add_row_down(wks, values):
    last_row = wks.get_as_df().shape[0] + 1
    wks.insert_rows(row=last_row, values=values)


#############################################################################


def space_cut(word):
    n = len(word)
    back = 0
    front = 0
    last_char = word[-1]
    first_char = word[0]
    while last_char == ' ' and back + 1 < n:
        back += 1
        last_char = word[-back - 1]
    while first_char == ' ' and front + 1 < n:
        front += 1
        first_char = word[front]
    return word[front:n - back]

def arg_min(A):
    m = 10e9
    mind = -1
    for i, e in enumerate(A):
        if m > e:
            m = e
            mind = i
    return mind, m

def get_sheet_id_from_link(link):
    idsearch = re.search(r'\/d\/[a-zA-Z0-9\-_]*', link)
    return idsearch.group(0)[3:]

def get_postfix(word):
    i = 0
    short_name = []
    while len(word) > - (i - 1) and word[i-1] != '_':
        i -= 1
        short_name += word[i]
    return ''.join(list(reversed(short_name)))

#def get_rows_in_df(df, column_name, value):
#    return df.loc[df[column_name] == value]


def get_row_by_keys(df, key_value=[], key_column=[], ratio='==', logic='&'):
    # TODO this sheet
    """ Like SQL quori

    :param df: pandas dataframe
    :param key_value: !format if int [2,3] if str ['"abs"', '"dfs"']
    :param key_column: colums where find keys 
    :return: row (if need special row[col_names] )
    """
    request = create_requst(key_column, ratio, logic)
    print(request.format(*key_value))
    try:
        return df.query(request.format(*key_value))
    except NameError:#as e: #SyntaxError
        print(1)#e.message)
        return df.query(request.format(*["\"" + i + "\"" for i in key_value]))
    except SyntaxError:
        print(2)  # e.message)
        req = request.format(*["\"" + i + "\"" for i in key_value])
        print(req, key_value)
        return df.query(req)


def get_blanc_row(df, parse_funk=None):
    """
    Get row with length equal number of columns ('' or if parse with default)
    :param df:
    :param parse_funk:  parse_funk(row) TODO add values the same as at df
    :return:
    """
    blanc_row = []
    for _ in df.columns:
        blanc_row.append('')
    return blanc_row

def get_dates(last_days_ago, a_interval, b_interval=7, weeks=16):
    """

    :param last_days_ago: start compute from now - days ago
    :param a_interval:
    :param b_interval:
    :param weeks: number of intervals
    :return: list of date trough a and b interval
    """
    last = datetime.now() - timedelta(days=last_days_ago)
    dates = []
    for i in range(weeks):
        a = last + timedelta(days=a_interval)
        last += timedelta(days=b_interval)
        dates.extend([a.strftime("%m-%d"), last.strftime("%m-%d")])
    return dates


def format_row(df, row_values, col_name, blanc_row=None):
    """
    Put row_values exactly in column (col_name)
    :param df:
    :param row_values: ['Denis', '109']
    :param col_name: ['Name', 'group']
    :param blanc_row: ['','','','']
    :return: ['','Denis', '', '109','']
    """
    formated_row = blanc_row.copy() or get_blanc_row(df)
    for value, col_name in zip(row_values, col_name):
        col_ind = df.columns.get_loc(col_name)
        formated_row[col_ind] = value
    return formated_row

def affilation_wks(short_name, graph_df):
    """ Find wich wks to use by postfix at command

    :param short_name: command last word like Basketball_FF1
    :param graph_df: pandas df of graph
    :return: node_id and link_id
    """
    row = get_row_by_keys(graph_df,
                          key_value=[short_name],
                          key_column=['node_short_name'])
    node = row['node'].values[0]
    if row['link'].values[0]:
        link = row['link'].values[0]
        return get_sheet_id_from_link(node), get_sheet_id_from_link(link)
    return get_sheet_id_from_link(node), None



def compute_distant(a,b):
    d = np.zeros([len(a)+1, len(b)+1])
    for i in range(len(a)):
        d[i, 0] = i
    for j in range(len(b)):
        d[0, j] = j

    for i in range(1, len(a)+1):
        for j in range(1, len(b)+1):
            if a[i-1] == b[j-1]:
                cost = 0
            else:
                cost = 1
            d[i, j] = min(d[i-1, j-1] + cost,  #substitution
                               d[i,   j-1] + 1,     #insertion
                               d[i-1, j  ] + 1)     #deletion
            if i > 1 and j > 1 and a[i-1] == b[j-2] and a[i-2] == b[j-1]:
                d[i, j]= min(d[i, j],
                              d[i - 2, j - 2] + cost) # transposition
    return max(d[len(a), len(b)], np.abs(len(a) - len(b)))

def sun_compute_distant(a, b):
    dst = compute_distant(a, b)
    alist = a.split()
    blist = b.split()
    if len(alist) > 1 and len(blist) > 1:
        if compute_distant(alist[0], blist[0]) < 2:
            if alist[1][0] == blist[1][0]:
                return min(2.0, dst)
            else:
                return min(3.0, dst)
    elif len(alist) == 1 and len(blist) > 0:
        if alist[0] == b.split()[0]:
            return 1.0
    return dst



if __name__ == "__main__":
    #wks = read_sheet('1kxwvaWNYHSCzD4LiTBg5vGDHFBmBrrjpnIpuqrgfzlw')
    #print('key' in wks.get_as_df().columns)
    print(get_dates(9, 3, 7))
    #print(wks.get_as_df().head())
    #transfer(wks, col_name=['Секция', 'Факультет'], new_col_name=['Перевод', 'Факультет'],
    #         key_val=['Тест Т Т',	'0'], key_col=['ФИО', 'Группа']
    #         )
    #print(get_sheet_id_from_link('https://docs.google.com/spreadsheets/d/1q8z_9QDwSia1IMo7qvDdH2cui0-D5My0xkClopMWcqw/edit#gid=0'))
    #print(re.search(r'\/d\/[a-zA-Z0-9\-_]*', 'wjw/js/d/asd-1-_2/efd'))


