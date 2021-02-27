# -*- coding:utf-8 -*-
"""
请求接口模块
"""

import requests
from interface_testing.udts_api_test.public_module.logger_module import logger


class RequestProcess(object):

    def __init__(self, url, params={}, headers={}, cookies={}, method='get', timeout=10):
        self.url = url
        self.params = params
        self.headers = headers
        self.cookies = cookies
        self.method = method
        self.timeout = timeout
        self.session = requests.Session()  # Session初始化

    def send_request(self, **params):
        """
        发送request请求，使用session保持会话
        :return:
        """
        url = params.get('url') or self.url
        params = params.get('params') or self.params
        method = params.get('method', '').upper() or self.method.upper()
        timeout = params.get('timeout') or self.timeout

        result = None
        try:
            # 请求接口
            if method == 'GET':
                resp = self.session.get(url=url, params=params, timeout=timeout)
            elif method == 'POST':
                resp = self.session.post(url=url, data=params, timeout=timeout)
            else:
                logger.warning(f'Undefined method - ({method})')
                return result
        except Exception as ex:
            logger.error(f'URL-({url}) request failed, error info: {ex}')
            return result

        # 获取返回内容
        if resp.status_code == 200:
            result = resp.json()
        else:
            logger.warning(f'URL-({url}) request failed, status code: {resp.status_code}')
        return result


if __name__ == '__main__':
    # 请求测试
    request = RequestProcess(url='http://127.0.0.1:8000/proxy/', params={'about': 'all'}, method='get')
    print(request.send_request())
