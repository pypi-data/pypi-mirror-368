# -*- coding: utf-8 -*-
import json
import chardet


def check_charset(code_data):
    # import chardet
    charset = chardet.detect(code_data)['encoding']
    print('charset: %s' % charset)
    return charset


def format_dict_style(data_dict):
    try:
        return json.dumps(data_dict, indent=4, sort_keys=True, ensure_ascii=False, default=str)
        # return json.dumps(data_dict, indent=4, sort_keys=True, ensure_ascii=False, default=str).encode('utf-8')
    except Exception as err:
        print('json.dumps error@itgeeker: %s' % err)

####################### deal list  #######################
# compare two list and return add and del list
def compare_lists_return_add_del(first_list, second_list):
    add_list = []
    del_list = []
    diff_list = list(
        set(first_list).symmetric_difference(
            set(second_list)))
    if diff_list:
        print('diff_list: %s' % diff_list)
        print('lists were different!!!')
        for diff in diff_list:
            if diff in first_list:
                del_list.append(diff)
            else:
                add_list.append(diff)
        print('add_list: %s' % add_list)
        print('del_list: %s' % del_list)
        return add_list, del_list
    else:
        return False, False