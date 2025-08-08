# -*- coding: utf-8 -*-
import os
from sys import platform


def generate_files_root_path(folder_usage, cur_db=None, o_main_ver=None):
    path_files_root = ''
    # cur_db = self.env.cr.dbname
    # o_main_ver = self.get_odoo_latest_ver()
    if platform == "linux" or platform == "linux2":
        # print('linux')
        path_files_root = os.path.join('/opt/odoo' + str(o_main_ver) + '/db_' + cur_db, folder_usage)
    elif platform == "win32":
        # print('# Windows...')
        path_files_root = os.path.join(r'D:\opt\odoo' + str(o_main_ver) + '\\db_' + cur_db, folder_usage)
    elif platform == "darwin":
        print('OS X, not setup now')
        path_files_root = os.path.join('/opt/odoo' + str(o_main_ver) + '/db_' + cur_db, folder_usage)
    if not os.path.isdir(path_files_root):
        os.makedirs(path_files_root)
    print('path_files_root@common: %s' % path_files_root)
    return path_files_root


####################### deal with agrs domain #######################
def replace_square_brackets(my_list):
    my_list_str = str(my_list)
    new_str = my_list_str.replace("[", "(").replace("]", ")")
    if new_str.startswith('(((') and new_str.endswith(')),)'):
        new_str = new_str.replace('(((', '[(').replace(')),)', ')]')
    print(f'new_str: {new_str}')
    new_list = eval(new_str)
    print(f'new_list type: {type(new_list)}')
    return new_list

####################### format data for postgresql sql #######################
def convert_dict_psql_up_date_arr(dict_data):
    arr = []
    for key, value in dict_data.items():
        # if type(value) is int:  # Handle Integers
        if type(value) in (int, float):  # Handle digits
            arr.append("{key} = {value}".format(key=key, value=value))
        else:  # Default Handler
            arr.append("{key} = '{value}'".format(key=key, value=value))
    # generate string from key/pair array
    data_arr = ", ".join(arr)
    print(f'data_arr: {data_arr}')
    return data_arr

def convert_dict_psql_insert_into_data_arr(dict_data):
    columns = dict_data.keys()
    values = [dict_data[column] for column in columns]
    # values = []
    # for column in columns:
    #     if dict_data[column] == 'NULL':
    #         values.append(None)
    #     else:
    #         values.append(dict_data[column])
    print(f"psql columns: {','.join(columns)}")
    print(f"psql values: {tuple(values)}")
    return ','.join(columns), tuple(values)


# print logger args
def _logger_print_args(fun_name, args, kwargs, staff_id=None):
    # _logger.warning(f'/*--*/ from function: {fun_name} for ID-{str(staff_id)} /*--*/')
    print('/*--*/ from function: %s for ID-%s /*--*/', fun_name,
                  staff_id if staff_id is not None else 'Unknown')
    if args:
        print(f'args: {args}')
    if kwargs:
        print(f'kwargs: {kwargs}')

# ####################### new env #######################
# def fetch_sql_result(query, params, db_name, fetch_one=False):
#     # db_name = self.env.cr.dbname
#     with registry(db_name).cursor() as new_cr:
#         try:
#             new_cr.execute(query, params)
#             if fetch_one:
#                 return new_cr.fetchone()
#             return new_cr.fetchall()
#         except Exception as e:
#             _logger.error(f"SQL 查询出错：{e}")
#             return None