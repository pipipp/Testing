# -*- coding:utf-8 -*-
"""
请求数据模块
"""

import requests
from interface_testing.udts_api_test.public_module.logger_module import logger


class RequestProcess(object):

    def __init__(self):
        self.session = requests.Session()  # Session初始化

    def send_request(self, url, request_data, method='GET', timeout=30, **params):
        """
        发送request请求，使用session保持会话
        :param url: 请求URL
        :param request_data: 请求数据
        :param method: 请求方法，默认GET
        :param timeout: 请求超时时间，默认30秒
        :param params: 额外参数，例如：Headers、cookie
        :return: result
        """
        result = dict(
            status=True,
            message='Success',
            data={}
        )

        try:
            # 请求接口
            if method.upper() == 'GET':
                resp = self.session.get(url=url, params=request_data, timeout=timeout)
            elif method.upper() == 'POST':
                resp = self.session.post(url=url, data=request_data, timeout=timeout)
            else:
                result['status'] = False
                result['message'] = f'Undefined method - ({method})'
                return result
        except Exception as ex:
            result['status'] = False
            result['message'] = f'URL-({url}) request failed, error info: {ex}'
            return result

        # 获取返回内容
        if resp.status_code == 200:
            result['data'] = resp.json()
        else:
            result['status'] = False
            result['message'] = f'URL-({url}) request failed, status code: {resp.status_code}'
        return result


if __name__ == '__main__':
    # 请求测试
    request = RequestProcess()
    print(request.send_request(url='http://127.0.0.1:8000/proxy/', request_data={'about': 'all'}))
