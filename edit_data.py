import util
from collections import defaultdict

MIN_DISTANCE = 2


def create_hash(main_key):
    hash_table = defaultdict(list)
    for key in main_key:
        hash_table[key[:2].lower()].append(key)
    return hash_table


def edit_key_by_nearest(new_key, hash_table_main_key):
    edited = []
    i = 0
    for key in new_key:
        dist = []
        #print(key, key[:2].lower(), hash_table_main_key)#, hash_table_main_key['гу'])
        cand_list = hash_table_main_key[key[:2].lower()]
        for cand in cand_list:
            dist.append(util.sun_compute_distant(cand.lower(), key.lower()))

        mind, minv = util.arg_min(dist)

        if dist and minv < MIN_DISTANCE:
            #    print(dist[-1], cand_list[arg_min(dist)], key)
            edited.append(cand_list[mind])
        else:
            i+= 1
            #print(key, minv, cand_list[mind])
            edited.append(key)

    #print(edited)
    return edited


def soft_edit_key_wks(wks_new, main_key, newkeycolname):
    new_df = wks_new.get_as_df()
    edited_key = edit_key_by_nearest(new_df[newkeycolname], create_hash(main_key))
    new_df[newkeycolname] = edited_key
    # print(edited_key)
    util.fill_sheet(wks_new, new_df)

### Parsing funk
def parse_anket(df, NODE_DICT):
    df = util.join_suname_to_init(df, crange=[2, 5], rrange=None, remove=True)
    df = df.rename(index=str, columns={"Фамилия": "ФИО",
                                       "Адрес электронной почты": "Почта",
                                       "Учебная группа": "Группа",
                                       "Секция по физкультуре": "Секция",
                                       "Медецинская группа, как на фотографии": "справка"
                                       })
    add_link(df, NODE_DICT, param1='Факультет', param2='Курс')
    return df

def edit_col_value(edited_fun, edited_wks, colname):
    df = edited_wks.get_as_df()
    df[colname] = edited_fun(df[colname])
    util.fill_sheet(edited_wks, df)

def remove_spaces(pandas_col):
    return pandas_col.apply(lambda x: ' '.join(x.split()))




def find_node_name(key, node_dict):
    if key in node_dict:
        return node_dict[key]
    else:
        return ''


def add_link(df, NODE_DICT, param1='Факультет', param2='Курс'):
    df['node_name'] = [find_node_name(str(a) + str(b), NODE_DICT)
                       for a, b in zip(df[param1], df[param2])]

### Sync









if __name__ == "__main__":
    """If you have full suname + name + ...  split it to 3 column then join_suname_to_init leave only one 
    table with 'Suname N T' then soft edit change it to nearest suname to cw - Control list   
    """

    #wks = util.read_sheet('1x-5iZFzVqHIAGjrQq6zQ7gIB689bO1ciDLK1Vhxz1Dc')
    #cw = util.read_sheet('1bpFPZyjwcz77SZp-7bFaqzO90nPJmrVXKrevUSJiW8I') # Control list
    #df = wks.get_as_df()

    #jdf =util.join_suname_to_init(df, crange=[1,4], rrange=None, remove=False)
    #soft_edit_key_wks(wks_new=wks, main_key=cw.get_as_df()['ФИО'], newkeycolname='ФИО')
    wks = util.read_sheet(util.get_sheet_id_from_link('https://docs.google.com/spreadsheets/d/124V-icrUEhI8WI6zP6Mrgk2R7JjK-KchI-mHYUXF4Xs/edit#gid=0'))
    ##cw = util.read_sheet('1HyUOq-jFXVx5nxZdXONEUasqIoq0PAFri9fXY3bd5gw')  # Control list
    #print(cw.get_as_df().head())
    ##soft_edit_key_wks(wks_new=wks, main_key=cw.get_as_df()['ФИО'], newkeycolname='ФИО')
    edit_col_value(remove_spaces, wks, "ФИО")