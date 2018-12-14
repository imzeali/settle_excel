# -*- coding: utf-8 -*-
# © 2018 WE Technology
# Authored by: Zhi Li (zealiemai@gmail.com)
import json
import md5
import os
import xlrd
from langid import langid

current_dirname = os.path.dirname(os.path.realpath(__file__))
data_dirname = '%s/data' % current_dirname


def get_dir_file(input_path, result, IGNORE_FILES=('.DS_Store')):
    #
    files = os.listdir(input_path)
    for file in files:
        if file not in IGNORE_FILES:

            if os.path.isdir(input_path + '/' + file):
                get_dir_file(input_path + '/' + file, result, IGNORE_FILES)
            else:
                result.append(input_path + '/' + file)


def get_dir_by_index(file_path, index):
    return file_path.split('/')[index]


def note_path_tree_process(str):
    # regex = re.compile(ur"[^\u4e00-\u9fa5a-zA-Z0-9/]")
    # str = regex.sub('', str)

    tree_str = '.'.join([md5.md5(x.encode('utf-8')).hexdigest() for x in str.split('/')])[1:]
    # path_list = [x for x in str.split('/')]
    # tree_list = [x for x in tree_str.split('.')]
    #
    # if len(tree_list) != len(path_list):
    #     print tree_str,path_list
    #     exit()
    # print str
    # print tree_str

    return tree_str


def node_path_deduce(row, i):
    if type(row[i + 1]) == unicode:
        node_path = row[i + 1]
    else:
        node_path = node_path_deduce(row, i + 1)

    return node_path


def is_first(row):
    return all([type(r) == unicode for r in row])


def get_node_id_and_path(row):
    node_id, node_path = None, None
    for i in range(0, len(row)):
        if type(row[i]) == float:
            node_id = int(row[i])
            node_path = node_path_deduce(row, i)

            if node_path[0:1] == '/':
                node_path = node_path[1:]

            if node_path[-1:] == '/':
                node_path = node_path[:-1]

            break

    if node_id is not None and node_path is not None and node_path is not '' and len(node_path) > 0 and is_first(
            row) is False:
        return [int(node_id), node_path, note_path_tree_process(node_path)]


def alias_by_str(str):
    return langid.classify(str)[0].upper()


def create_table_a(data, sheets, table_a_json):
    # 节点数据表
    if len(sheets) >= 2:
        table_1 = data.sheet_by_index(1)
        for item in range(table_1.nrows):
            row = table_1.row_values(item)
            id_path = get_node_id_and_path(row)
            if id_path:
                if country_code == 'JP':
                    alias = 'EN' if alias_by_str(id_path[1]) == 'EN' else None
                else:
                    alias = None

                json_data = {"country_code": country_code, "node_id": id_path[0], "node_path": id_path[1],
                             "node_path_tree": id_path[2], "alias": alias}
                table_a_json.append(json_data)

                # if id_path[0] ==14223257031:
                #     print json_data

    return table_a_json


def create_table_b(data, sheets, table_b_json):
    # 属性数据表
    if len(sheets) >= 3:
        table_2 = data.sheet_by_index(2)
        for item in range(table_2.nrows):
            row = table_2.row_values(item)
            if is_first(row) == False:
                table_b_json.append(
                    {"country_code": country_code, "node_id": int(row[0]), "node_name": row[1],
                     "refinement_name": row[2], "attribute": row[3], "modifiers": row[5]})


def create_table_c(data, sheets, table_c_json):
    if len(sheets) >= 3:

        sheet_refinements = data.sheet_by_index(2)
        name_map_dict = excel_name_map_dict(data)
        for item in range(sheet_refinements.nrows):
            node_value_index = sheet_refinements.cell(item, 4).value
            row = sheet_refinements.row_values(item)
            if  is_first(row) is False:
                valus = get_scope_by_value_index(name_map_dict, node_value_index)
                table_c_json.append({"node_id": int(row[0]), "attribute": row[3], "valus": valus})


def excel_name_map_dict(excel_data):
    name_map_dict = {}
    for name, map in excel_data.name_map.items():
        # print map[0].__dict__
        start_row_index = map[0].result.value[0].coords[2]
        end_row_index = map[0].result.value[0].coords[3]
        name_map_dict.setdefault(name, (start_row_index, end_row_index))
        # print type(map[0].result)
    return name_map_dict


def get_scope_by_value_index(name_map_dict, node_value_index):
    sheet_db = data.sheet_by_index(3)
    if node_value_index and name_map_dict.has_key(node_value_index):
        valus_postion = name_map_dict[node_value_index]
        valus = []
        for i in range(valus_postion[0], valus_postion[1]):
            valus.append(sheet_db.row_values(i)[0])
        return valus
    else:
        return []


if __name__ == "__main__":
    file_paths = []
    ignore_files = []
    get_dir_file(data_dirname, file_paths)
    file_paths = file_paths
    table_a_json = []
    table_b_json = []
    table_c_json = []
    for file in file_paths:
        if os.path.getsize(file) > 0:
            country_code = get_dir_by_index(file, -2)
            data = xlrd.open_workbook(file, 'rb')
            sheets = data.sheets()
            # create_table_a(data, sheets, table_a_json)
            # create_table_b(data,sheets,table_b_json)
            create_table_c(data, sheets, table_c_json)

    table_a = json.dumps(table_a_json)
    f = open('export/table_a.json', 'w')
    f.write(table_a)
    f.close()

    table_b = json.dumps(table_b_json)
    f = open('export/table_b.json', 'w')
    f.write(table_b)
    f.close()
    table_c = json.dumps(table_c_json)
    f = open('export/table_c.json', 'w')
    f.write(table_c)
    f.close()
