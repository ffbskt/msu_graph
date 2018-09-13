import json
import util
import edit_data as ed
NODE_DICT = {'Физический1': "закрытый_список_2017"}
PARSE_FUNK = {'joinNameAddLink': ed.parse_anket}
"""
Go by graph and sync all linked sheets by args.
"""








class Graph:
    def __init__(self, graph_df):
        self.graph = graph_df

    def open_node_by_name(self, node_name):
        row = util.get_row_by_keys(self.graph, key_column=["node_name"], key_value=[node_name])
        # print(node_name, 'r=', row)
        assert not row.empty, Exception("Can't find link_name [{}] in graph".format(node_name))
        link = row["node"].values[0]
        return util.read_sheet(util.get_sheet_id_from_link(link))


    def sync_straight(self, df, link_col, args, add_key=False):
        print('s', link_col)
        for link_val in link_col.split():
            unique = list(df[link_val].unique())
            if '' in unique:
                unique.remove('')
            while unique:
                main_name = unique.pop()
                main_wks = self.open_node_by_name(main_name)
                from_df = df[df[link_val] == main_name]
                #print(from_df[:10], main_wks)
                util.sync_by_colname(from_wks=from_df, to_wks=main_wks, **args)
                if add_key:
                    self.add_key(from_df, main_wks, args["to_key_colname"])


    def add_key(self, fdf, twks, key_col):
        new_key = []
        tdf = twks.get_as_df()
        last_row = None
        blanc_row = util.get_blanc_row(tdf)
        for i, key in fdf[key_col].iterrows():
            # print(key.values)
            # print(util.get_row_by_keys(tdf, key.values, key_col).empty)
            if util.get_row_by_keys(tdf, key.values,
                                    key_col).empty:  # util.get_row_by_keys(tdf, key.values[0], key_col):
                print('ok,', key.values)
                row = util.format_row(tdf, list(key.values), key_col, blanc_row)
                new_key.append(row)
                last_row = twks.get_as_df().shape[0] + 1
        if last_row is not None:
            twks.insert_rows(row=last_row, values=new_key)

    # add_key(clean_f, twks, key_col)

    def sync_edge(self, line):
        args = json.loads(line['args'])
        #print('p',len(line['node'].split()))#Баскетбол_Волконский_Д_А_ФФ1
        print("sssss", args)
        if len(line['node'].split()) > 1:
            #print('@', len(line['node']))
            self.one_to_many_sync(one_node=line['link'], many_node=line['node'],
                              args=args, one_node_to_many_link=False)
        elif len(line['link'].split()) > 1:
            #print(1, line['node'])
            self.one_to_many_sync(one_node=line['node'], many_node=line['link'],
                                  args=json.loads(line['args']), one_node_to_many_link=True)
        elif len(line['link'].split()) == 1 and len(line['node'].split()) == 1:
            print(123, line['node'], line['link'], args)
            to_wks = util.read_sheet(util.get_sheet_id_from_link(line['link']))
            form_wks = util.read_sheet(util.get_sheet_id_from_link(line['node']))
            util.sync_by_colname(from_wks=form_wks, to_wks=to_wks, **args)
            # self.one_to_many_sync(one_node=line['node'], many_node=line['link'],
            #                      args=json.loads(line['args']), one_node_to_many_link=True)
        else:
            from_wks = util.read_sheet(util.get_sheet_id_from_link(line['node']))
            if line['parse_funktion']:
                from_df = PARSE_FUNK[line['parse_funktion']](from_wks.get_as_df(), NODE_DICT)
            else:
                from_df = from_wks.get_as_df()

            add_key = line["can_add_key"]
            print('s e')
            self.sync_straight(df=from_df, link_col=line['straight_link_col'], args=args, add_key=add_key)

    def one_to_many_sync(self, one_node, many_node, args={}, one_node_to_many_link=True):
        print(one_node)
        one_wks = util.read_sheet(util.get_sheet_id_from_link(one_node))
        many_links = many_node.split()
        for link in many_links:
            if link:
                one_of_many_wks = util.read_sheet(util.get_sheet_id_from_link(link))
                print(args['to_values_colname'], one_node, many_node)
                if one_node_to_many_link:
                    util.sync_by_colname(from_wks=one_wks, to_wks=one_of_many_wks, **args)
                else:
                    util.sync_by_colname(from_wks=one_of_many_wks, to_wks=one_wks, **args)




    def sync_all(self):
        for i, line in graph.iterrows():
            print('l i=', i, ' pass=', line['Pass'])
            if line['Pass']:
                continue
            self.sync_edge(line)



if __name__ == "__main__":
    #graph = util.read_sheet('1MeAYhENafzQMoTKDG-VOLI308ih1wl7SjMLbOkwJU4M').get_as_df()
    #graph = util.read_sheet('1q8z_9QDwSia1IMo7qvDdH2cui0-D5My0xkClopMWcqw').get_as_df()  # TEST
    graph = util.read_sheet('1sqMrcxNvbLna3BHbzQEj-W3ivVBmUPQQ4aPQhp1kW5M').get_as_df()
    #graph = util.read_sheet('1ZR38L8tFMdUTODVQ0cdz79jPKX4xpNn7R11S82u5Jyk').get_as_df()

    g = Graph(graph)
    g.sync_all()
