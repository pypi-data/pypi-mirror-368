# -*- coding: utf-8 -*-
import json
import os
import tempfile
import time
from datetime import datetime, timezone


####################### operate dict to json  file #######################
def save_data_to_ffp(prefix, staff_id, data, save_remark=None):
    tmp_path = tempfile.gettempdir()
    target_ffp = os.path.join(tmp_path, prefix + str(staff_id) + '.json')
    print(f'save zl to target_ffp: {target_ffp}')
    if not os.path.isfile(target_ffp):
        try:
            save_dict = {
                'list': [data],
            }
            utc_now = datetime.now(timezone.utc)
            save_dict['save_utc_timestamp'] = utc_now.timestamp()
            if save_remark:
                save_dict['save_remark'] = save_remark
            print(f'save_dict final: {json.dumps(save_dict, indent=4, sort_keys=True)}')
            retried_save = 8
            tried_time = 0
            while tried_time < retried_save:
                try:
                    with open(target_ffp, 'wb') as jf_new:
                        jf_new.write(
                            json.dumps(save_dict, indent=4, sort_keys=True, ensure_ascii=False, default=str).encode(
                                'utf-8'))
                    return True
                except (IOError, OSError) as err:
                    print(f"file is occupied @save zl to ffp:{err}")
                except Exception as err:
                    print('err@save zl to ffp: %s' % err)
                time.sleep(0.5)
                tried_time += 1
                if tried_time > retried_save:
                    print(f"'retried save zl to ffp failed for: ID-{staff_id}")
                    return False
        except Exception as err:
            print('err@save zl to json ffp: %s' % err)
            return False
    else:
        update_data_to_ffp(prefix, staff_id, data, update_remark='update existed zl ffp')


def update_data_to_ffp(prefix, staff_id, data_new, update_remark=None):
    tmp_path = tempfile.gettempdir()
    target_ffp = os.path.join(tmp_path, prefix + str(staff_id) + '.json')
    print(f'update to target_ffp: {target_ffp}')
    try:
        with open(target_ffp, 'rb') as jf_old:
            updated_dict = json.loads(jf_old.read())
        # for k, v in dict_up_data.items():
        #     updated_dict[k] = v
        # data_list = updated_dict['data_list']
        data_list = updated_dict.get('data_list', [])

        # for none dedup
        if data_new not in data_list:
            data_list.append(data_new)

        # # for dedup
        # data_newnone_read_list = []
        # for zl in data_list:
        #     if 'is_read' in zl:
        #         data_newrm_read = {k: v for k, v in zl.items() if k != 'is_read'}
        #         data_newnone_read_list.append(data_newrm_read)
        #     else:
        #         data_newnone_read_list.append(zl)
        # print(f'data_newnone_read_list: {data_newnone_read_list}')
        # if data_newnone_read_list:
        #     if data_new not in data_newnone_read_list:
        #         data_list.append(data_new)
        #     else:
        #         _logger.info('/*-' * 6 + ' data_new already in data_list ' + '-*' * 6)
        # else:
        #     data_list.append(data_new)

        utc_now = datetime.now(timezone.utc)
        updated_dict['update_utc_timestamp'] = utc_now.timestamp()
        if update_remark:
            updated_dict['update_remark'] = update_remark
        print(f'updated zl dict final: {json.dumps(updated_dict, indent=4, sort_keys=True)}')
        retried_up = 8
        tried_time = 0
        while tried_time < retried_up:
            try:
                with open(target_ffp, 'wb') as jf_new:
                    jf_new.write(
                        json.dumps(updated_dict, indent=4, sort_keys=True, ensure_ascii=False, default=str).encode(
                            'utf-8'))
                return True
            except (IOError, OSError) as err:
                print(f"file is occupied @update zl to ffp:{err}")
            except Exception as err:
                print('err@update zl to ffp: %s' % err)
            time.sleep(0.5)
            tried_time += 1
            if tried_time > retried_up:
                print(f"'retried update zl to ffp failed for: ID-{staff_id}")
                return False
    except Exception as err:
        print('err@update dict ffp zl json ffp: %s' % err)
        return False


def _get_and_delete_first_cmd(data_dict, cmd_key, not_del=None):
    if cmd_key not in data_dict or not isinstance(data_dict[cmd_key], list) or not data_dict[cmd_key]:
        return False

    # for none dedup
    else:
        first_cmd = data_dict[cmd_key][0]
        print("First cmd:", first_cmd)
        if not not_del:
            data_dict[cmd_key].pop(0)
            print(f'data_dict: {data_dict}')
        return first_cmd

    # # for dedup
    # cmd_list = [x for x in data_dict[cmd_key] if 'is_read' not in x]
    # print(f'cmd_list: {cmd_list}')
    # if not cmd_list:
    #     return None
    # else:
    #     first_cmd = cmd_list[0]
    #     # first_cmd = data_dict[cmd_key][0]
    #     print("First cmd:", first_cmd)
    #     if not not_del:
    #         # data_dict[cmd_key].pop(0)
    #         first_cmd['is_read'] = True
    #         print(f'data_dict: {data_dict}')
    #     return first_cmd


def read_data_to_ffp(prefix, staff_id, key_n, not_del=None):
    tmp_path = tempfile.gettempdir()
    target_ffp = os.path.join(tmp_path, prefix + str(staff_id) + '.json')
    print(f'read zl from target_ffp: {target_ffp}')
    if not os.path.isfile(target_ffp):
        return False
    try:
        with open(target_ffp, 'rb') as jf_old:
            read_dict = json.loads(jf_old.read())
        # print(f'read_dict: {read_dict}')
        first_cmd = _get_and_delete_first_cmd(read_dict, key_n, not_del)
        print(f'read_dict after read and rm: {json.dumps(read_dict, indent=4, sort_keys=True)}')
        retried_read = 8
        tried_time = 0
        while tried_time < retried_read:
            try:
                with open(target_ffp, 'wb') as jf_new:
                    jf_new.write(
                        json.dumps(read_dict, indent=4, sort_keys=True, ensure_ascii=False, default=str).encode(
                            'utf-8'))
                    return first_cmd
            except (IOError, OSError) as err:
                print(f"file is occupied @read zl to ffp:{err}")
            except Exception as err:
                print('err@read zl to ffp: %s' % err)
            time.sleep(0.5)
            tried_time += 1
            if tried_time > retried_read:
                print(f"'retried read zl to ffp failed for: ID-{staff_id}")
                return False
    except Exception as err:
        print('err@read dict ffp zl json ffp: %s' % err)
        return False


####################### deal with file write and open read #######################
# tmp_ffp = os.path.join(tmp_path, 'dw_dealer_' + str(dealer_id) + 'latest_verify')

def try_os_remove_ffp(file_ffp):
    retried_del = 8
    tried_time = 0
    while tried_time < retried_del:
        try:
            os.remove(file_ffp)
            return True
        except PermissionError as err:
            print(f'err@try os remove ffp PermissionError-(indicating the file is occupied: {err}')
            time.sleep(0.5)
            tried_time += 1
            if tried_time > retried_del:
                print(f"'retried os remove ffp failed for ffp: {file_ffp}")
                return False
        except Exception as err:
            print('err@try os remove ffp(%s) failed: %s' % (file_ffp, err))
            return False


def check_ffp_existed(prefix, staff_id, validity_seconds=2):
    tmp_path = tempfile.gettempdir()
    target_ffp = os.path.join(tmp_path, prefix + str(staff_id) + '.json')
    print(f'check ffp existed: {target_ffp}')
    if os.path.isfile(target_ffp):
        with open(target_ffp, 'rb') as jf:
            res_value = json.loads(jf.read())
            create_ts = res_value.get('cur_utc_timestamp', None)
            create_dt = datetime.fromtimestamp(create_ts)
            # now_ts = (datetime.now(timezone.utc)).timestamp()
            # now_dt = datetime.fromtimestamp(int_timestamp)
            now_dt = datetime.now()
            ts_diff = (now_dt - create_dt).total_seconds()
            print('ts_diff: %s' % ts_diff)
            if ts_diff > validity_seconds:
                return False
        return True
    return False


def save_dict_data_to_ffp(prefix, staff_id, dict_data, save_remark=None):
    tmp_path = tempfile.gettempdir()
    target_ffp = os.path.join(tmp_path, prefix + str(staff_id) + '.json')
    print(f'save to target_ffp: {target_ffp}')
    utc_now = datetime.now(timezone.utc)
    dict_data.update({
        'cur_utc_timestamp': utc_now.timestamp()
    })
    if save_remark:
        dict_data.update({
            'save_remark': save_remark
        })
    # with open(target_ffp, 'wb') as jf:
    #     jf.write(json.dumps(dict_data, indent=4, sort_keys=True, ensure_ascii=False, default=str).encode('utf-8'))
    retried_save = 6
    tried_time = 0
    while tried_time < retried_save:
        try:
            with open(target_ffp, 'wb') as jf:
                jf.write(
                    json.dumps(dict_data, indent=4, sort_keys=True, ensure_ascii=False, default=str).encode('utf-8'))
            return True
        except (IOError, OSError) as err:
            print(f"file is occupied @save dict to ffp:{err}")
            time.sleep(0.5)
            tried_time += 1
            if tried_time > retried_save:
                print(f"'retried save dict to ffp failed for: ID-{staff_id}")
                return False
        except Exception as err:
            print('err@write dict to ffp: %s' % err)
            return False
    return True


def read_dict_value_from_ffp(prefix, staff_id, last_stmp=None, dict_key=None, del_pr=False, not_del=False):
    tmp_path = tempfile.gettempdir()
    source_ffp = os.path.join(tmp_path, prefix + str(staff_id) + '.json')
    # print(f'read from source_ffp: {source_ffp}')
    try:
        if not os.path.isfile(source_ffp):
            return False
        elif prefix in (
                'dw_api_restart_',
                'dw_api_pr_',
                'dw_close_tbl_',
                'dw_ws_tmnt_data_new',
                'dw_ws_tmnt_poker_test_',
                'dw_ws_tmnt_poker_verify_'
        ):
            return True
        else:
            with open(source_ffp, 'rb') as jf:
                res_value = json.loads(jf.read())
                if dict_key:
                    res_value = res_value.get(dict_key, None)
                    return res_value
            print(f'res_value: {res_value}')
            # if last_stmp <= res_value.get('cur_utc_timestamp', None):
            #     return res_value
            # return False
            return res_value
    except Exception as err:
        print(f'err@read source_ffp failed: %s' % err)
        return False
    finally:
        if os.path.isfile(source_ffp) and prefix != 'dw_api_pr_' and not not_del:
            # os.remove(source_ffp)
            try_os_remove_ffp(source_ffp)
        if del_pr:
            # os.remove(source_ffp)
            try_os_remove_ffp(source_ffp)


def del_ffp(prefix, staff_id):
    tmp_path = tempfile.gettempdir()
    target_ffp = os.path.join(tmp_path, prefix + str(staff_id) + '.json')
    print(f'del zl ffp: {target_ffp}')
    if os.path.isfile(target_ffp):
        retried_del = 8
        tried_time = 0
        while tried_time < retried_del:
            try:
                os.remove(target_ffp)
                return True
            except PermissionError as err:
                print(f'err@del zl ffp PermissionError-(indicating the file is occupied: {err}')
                time.sleep(0.5)
                tried_time += 1
                if tried_time > retried_del:
                    print(f"'retried del ffp failed for: ID-{staff_id}")
                    return False
            except Exception as err:
                print('err@del ffp(%s) failed: %s' % (target_ffp, err))
                return False
    else:
        return True