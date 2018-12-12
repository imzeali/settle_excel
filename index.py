# -*- coding: utf-8 -*-
# © 2018 WE Technology
# Authored by: Zhi Li (zealiemai@gmail.com)
import json
import os
import re

import xlrd

current_dirname = os.path.dirname(os.path.realpath(__file__))
data_dirname = '%s/data' % current_dirname


def get_dir_file(input_path, result, IGNORE_FILES=()):
    #
    files = os.listdir(input_path)
    for file in files:
        if file not in IGNORE_FILES:

            if os.path.isdir(input_path + '/' + file):
                get_dir_file(input_path + '/' + file, result, ())
            else:
                result.append(input_path + '/' + file)


def get_dir_by_index(file_path, index):
    return file_path.split('/')[index]


def note_path_tree_process(str):
    regex = re.compile(ur"[^\u4e00-\u9fa5a-zA-Z0-9/]")
    str = regex.sub('', str)

    return '.'.join(str.split('/'))[1:]


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
            break

    if node_id is not None and node_path is not None or is_first(row) is False:
        return [node_id, node_path, note_path_tree_process(node_path)]


if __name__ == "__main__":
    file_paths = []
    ignore_files = []
    get_dir_file(data_dirname, file_paths)
    file_paths = file_paths
    table_1_json = []
    for file in file_paths:
        if os.path.getsize(file) > 0:
            country_code = get_dir_by_index(file, -2)
            data = xlrd.open_workbook(file, 'rb')
            sheets = data.sheets()
            # 节点数据
            if len(sheets) >= 2:
                table_1 = data.sheet_by_index(1)
                for item in range(table_1.nrows):
                    row = table_1.row_values(item)
                    id_path = get_node_id_and_path(row)

                    if id_path:
                        table_1_json.append(
                            {"country_code": country_code, "node_id": id_path[0], "node_path": id_path[1],
                             "node_path_tree": id_path[2]})

    table_a = json.dumps(table_1_json)
    f = open('export/table_a.json', 'w')
    f.write(table_a)
    f.close()

    # if len(sheets)>=3:
    #     table_2 = data.sheet_by_index(2)
    #
    #     # 属性数据
    #     for item in range(table_2.nrows):
    #         row = table_2.row_values(item)
    #         # note_id = row[1]
    #         # note_path = note_path_process(row[2])
    #         print(country_code,row)
