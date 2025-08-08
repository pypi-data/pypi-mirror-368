# -*- coding: utf-8 -*-
import json
import time


def check_key_existed_from_cache(r_conn, prefix, staff_id):
    # redis_pwd = self.env["ir.config_parameter"].sudo()._api_get_parameter_redis_pwd()
    # r_obj = DwRedisPool(port=6379, db=0, password=redis_pwd)
    # r = r_obj.get_redis_connection()
    r = r_conn.get_redis_connection()
    if not r:
        return False
    else:
        user_key = prefix + str(staff_id)
        if r.exists(user_key):
            return True
        return False


def save_data_to_cache(r_conn, prefix, staff_id, dict_data, r_type='hash', save_remark=None, ffp=None):
    # r = self.connect_to_redis_srv()
    # redis_pwd = self.env["ir.config_parameter"].sudo()._api_get_parameter_redis_pwd()
    # r_obj = DwRedisPool(port=6379, db=0, password=redis_pwd)
    # r = r_obj.get_redis_connection()
    r = r_conn.get_redis_connection()
    # print('save_data_to_cache r: %s' % r)
    print(f'r@save_data_to_cache: {r}')
    if not r:
        return False
    else:
        user_key = prefix + str(staff_id)
        # zl_timestamp = str(int(time.time()))
        zl_timestamp = str(time.time())
        if save_remark:
            dict_data['save_remark'] = save_remark
        # dict_data_str = json.dumps(dict_data)
        dict_data_str = json.dumps(dict_data, indent=4, sort_keys=True, ensure_ascii=False, default=str).encode('utf-8')
        # r_save_zl = r.hset(user_key, zl_timestamp, dict_data_str)
        # if r_save_zl:
        #     print(f'save success, timestamp: {zl_timestamp}')
        # else:
        #     print(f'save zl data to cache failed, timestamp: {prefix}_{staff_id}-{zl_timestamp}-{dict_data_str}')
        #     return False

        # del existed key if type diff
        if r.exists(user_key):
            current_type = r.type(user_key).decode('utf-8')
            # print(f'current_type: {current_type}')
            # print(f'r_type: {r_type}')
            # print(f"Current type of user_key '{user_key}': {current_type}")
            if current_type != r_type:
                r.delete(user_key)
                print(f"Deleted user_key '{user_key}' because its type was different.")

        retried_save = 3
        tried_time = 0
        while tried_time < retried_save:
            try:
                if r_type == 'hash':
                    r_save_zl = r.hset(user_key, zl_timestamp, dict_data_str)
                # elif r_type == 'string':
                else:
                    r_save_zl = r.set(user_key, dict_data_str)
                if r_save_zl:
                    # print(f'save success@cache: {user_key} - {zl_timestamp}')
                    # time.sleep(0.01)
                    return True
            except Exception as err:
                print(
                    f'err@save zl data to cache failed: {prefix}_{staff_id}-{zl_timestamp}-{dict_data_str}---{err}')
                tried_time += 1
                if tried_time > retried_save:
                    print(f"'retried save failed zl data: {json.dumps(dict_data, indent=4, sort_keys=True)}")
                    return False
                backoff = tried_time * 2
                print(f'Retrying in {backoff} seconds: count={tried_time}')
                time.sleep(backoff)


def del_field_line_from_cache(r, uk, f):
    retried_del = 3
    tried_time = 0
    while tried_time < retried_del:
        try:
            r_del = r.hdel(uk, f)
            if r_del:
                print(f'del field line from cache success, r_del: {r_del}')
                return True
        except Exception as err:
            print(
                f'del field line from cache failed, user key: {uk} and field: {f}---{err}')
            tried_time += 1
            if tried_time > retried_del:
                print(f"'retried del failed, user key: {uk} and field: {f}")
                return False
            backoff = tried_time * 2
            print(f'Retrying in {backoff} seconds: count={tried_time}')
            time.sleep(backoff)


# not del for line del, del pre for del key
def read_data_from_cache(r_conn, prefix, staff_id, not_del=None, del_pr=False):
    # r = self.connect_to_redis_srv()
    # redis_pwd = self.env["ir.config_parameter"].sudo()._api_get_parameter_redis_pwd()
    # r_obj = DwRedisPool(port=6379, db=0, password=redis_pwd)
    # r = r_obj.get_redis_connection()
    r = r_conn.get_redis_connection()
    if not r:
        return False
    else:
        user_key = prefix + str(staff_id)
        if r.exists(user_key):
            print(f"user key@read '{user_key}' existed")
            try:
                if prefix == 'dw_api_recovery_':
                    r_val = r.get(user_key)
                    return json.loads(r_val.decode('utf-8'))
                elif prefix in (
                        'dw_api_restart_',
                        'dw_api_pr_',
                        'dw_close_tbl_',
                        'dw_ws_tmnt_zl_',
                ):
                    return True
                else:
                    r_all_field = r.hkeys(user_key)
                    if len(r_all_field) == 1:
                        print('only one data')
                        r_field = float(r_all_field[0])
                    else:
                        print('more than one data')
                        sorted_list = sorted([float(x) for x in r_all_field])
                        r_field = sorted_list[0]
                    if r_field:
                        print(f'r_field: {r_field}')
                        r_val = r.hget(user_key, str(r_field))
                        print(f'r_val: {r_val}')
                        if not not_del:
                            # r_del = r.hdel(user_key, str(r_field))
                            del_field_line_from_cache(r, user_key, str(r_field))
                        return json.loads(r_val.decode('utf-8'))
            except Exception as err:
                print(f'read data from cache failed, user key: {user_key}---{err}')
                return False
            finally:
                if prefix in (
                        'dw_api_restart_',
                        # 'dw_api_pr_',
                        'dw_close_tbl_',
                        'dw_ws_tmnt_zl_',
                        # 'dw_ws_tmnt_poker_test_',
                        # 'dw_ws_tmnt_poker_verify_'
                ) and not not_del:
                    del_key_from_r(prefix, staff_id)
                if del_pr:
                    del_key_from_r(prefix, staff_id)
        else:
            # print(f"user key '{user_key}' not existed, no zl found!!!")
            return False


def del_key_from_r(r_conn, prefix, staff_id):
    # r = self.connect_to_redis_srv()
    # redis_pwd = self.env["ir.config_parameter"].sudo()._api_get_parameter_redis_pwd()
    # r_obj = DwRedisPool(port=6379, db=0, password=redis_pwd)
    # r = r_obj.get_redis_connection()
    r = r_conn.get_redis_connection()
    # r.ping()
    if not r:
        return False
    else:
        user_key = prefix + str(staff_id)
        print(f'user key@del: {user_key}')
        if r.exists(user_key):
            print(f"user key '{user_key}' existed")
            retried_del = 3
            tried_time = 0
            while tried_time < retried_del:
                r_del = r.delete(user_key)
                print(f'delete result: {r_del}')
                if r_del:
                    print(f'del success for user key: {user_key}')
                    # time.sleep(0.01)
                    return True
                else:
                    print(
                        f'del zl data from cache failed for {user_key}')
                    tried_time += 1
                    if tried_time > retried_del:
                        print(f"'retried del key failed for: {user_key}")
                        return False
                    backoff = tried_time * 2
                    print(f'Retrying in {backoff} seconds: count={tried_time}')
                    time.sleep(backoff)
            print(f'del finished!!!')
        else:
            return True
