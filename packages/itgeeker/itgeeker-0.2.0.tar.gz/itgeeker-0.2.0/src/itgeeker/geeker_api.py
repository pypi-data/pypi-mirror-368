# -*- coding: utf-8 -*-

import time
import requests
import logging
_logger = logging.getLogger(__name__)


class GeekerApi:

    ####################### return data format #######################
    def format_return_data(self, isSuccess=True, errMsg='success', data=None, status=None, err_desc=None, isToast=None):
        data_returned = {
            'isSuccess': isSuccess,
            'errMsg': errMsg
        }
        if isToast:
            data_returned.update({
                'isToast': True
            })
        if data:
            data_returned.update({
                'data': data
            })
        if status:
            data_returned.update({
                'status': status
            })
        if err_desc:
            data_returned.update({
                'err_description': err_desc
            })
        # return json.dumps(error_returned_data)
        return data_returned

    ####################### dw post with tries #######################
    def send_post_with_retry(self, url, data, headers=None, max_retries=3, retry_interval=3):
        for i in range(max_retries):
            try:
                response = requests.post(url, data=data, headers=headers)
                response.raise_for_status()  # 抛出异常处理 HTTP 错误
                # return response
            except requests.exceptions.RequestException as err:
                _logger.warning(f"post data to srv failed: {err}")
                if i < max_retries - 1:
                    print(f"this is {i + 1} times failed request, try again in {retry_interval} seconds ...")
                    time.sleep(retry_interval)
                else:
                    _logger.warning(f"Retry {max_retries} times and fail, then give up")
                    raise  # 重新抛出异常，让调用者处理
                    # return False

    ####################### dw print httprequest info #######################
    def print_httprequest_info(self, req_quest_env, source):
        _logger.debug('/*-' * 8 + f'request httprequest source: {source}' +  '-*/' * 8)
        try:
            # _logger.info(f'request.session.sid@bus ws cntller: {request.session.sid}')
            # http_cookie = req_quest_env['HTTP_COOKIE']
            # _logger.info(f'from game srv http_cookie: {http_cookie}')
            # HTTP_COOKIE 'session_id=

            # http_authorization = req_quest_env['HTTP_AUTHORIZATION']
            # _logger.info(f'from game srv http_authorization: {http_authorization}')
            # http_authorization: Basic bzE2X2R3OjZjMDJjZDU0LWFiN2MtNDAyNy1iMjVlLTYyYzFlZWRlZjk1ZA ==

            http_user_agent = req_quest_env.get('HTTP_USER_AGENT', '')
            _logger.debug(f'http_user_agent: {http_user_agent}')
            # http_user_agent: PostmanRuntime/7.40.0

            # no these keys
            # client_ip_x = req_quest_env['X-Forwarded-For']
            # x_real_ip = req_quest_env['x-real-ip']
            # x_forwarded_host = req_quest_env['X-Forwarded-Host']

            remote_addr = req_quest_env.get('REMOTE_ADDR', '')
            _logger.info(f'remote_addr: {remote_addr}')

            http_host = req_quest_env.get('HTTP_HOST', '')
            _logger.debug(f'http_host: {http_host}')
        except Exception as err:
            _logger.error('err@logger request env params: %s' % err)
