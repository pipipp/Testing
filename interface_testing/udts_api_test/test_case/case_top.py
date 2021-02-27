# -*- coding:utf-8 -*-
"""
Test Case 父类（包含所有的公共方法）
"""
import unittest

from urllib.parse import urljoin
from interface_testing.udts_api_test.public_module.logger_module import logger
from interface_testing.udts_api_test.public_module.request_module import RequestProcess


class CaseTop(unittest.TestCase):

    def setUp(self):
        """在每个测试方法之前执行"""
        pass

    def tearDown(self):
        """在每个测试方法之后执行"""
        pass

    def start_case(self, **params):
        """
        启动用例测试
        :param params:
        :return:
        """
        # 发送请求
        process = RequestProcess()
        url = urljoin(params['api_host'], params['request_url'])
        resp = process.send_request(url=url, request_data=params['request_data'],
                                    method=params['request_method'])

        # 判定请求是否成功收到数据
        self.assertTrue(resp['status'], msg=resp['message'])

        # 判定请求结果是否符合预期结果
        check_point = {}
        for condition in params['check_point'].split('&'):  # 整合所有的预期结果
            key, value = condition.split('=')
            check_point[key.strip()] = value.strip()

        data = resp['data']
        for key, value in check_point.items():
            self.assertTrue(data.get(key), msg=f'返回内容缺少-({key}), 实际返回内容：{data}')
            self.assertEqual(str(data[key]), value, msg=f'返回值不匹配-({value}), 实际返回内容：{data[key]}')
