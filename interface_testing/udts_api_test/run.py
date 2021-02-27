# -*- coding:utf-8 -*-
import os
import datetime
import unittest
import HtmlTestRunner


from interface_testing.udts_api_test.public_module.logger_module import logger
from interface_testing.udts_api_test.settings import PROJECT_DIR


class RunTestCase(object):

    def __init__(self):
        # 测试脚本
        self.case_path = PROJECT_DIR['test_case_dir']  # 测试脚本所在目录
        self.execute_script_pattern = 'test_*.py'  # 定义需要启动哪些测试脚本

        # 输出报告（按天生成文件夹）
        self.report_path = os.path.join(PROJECT_DIR['result_dir'], datetime.datetime.now().strftime('%Y-%m-%d'))
        self.report_name = 'udts'

    def main(self):
        """执行测试用例"""
        discover = unittest.defaultTestLoader.discover(start_dir=self.case_path, pattern=self.execute_script_pattern)
        runner = HtmlTestRunner.HTMLTestRunner(output=self.report_path, report_name=self.report_name,
                                               report_title='Test Report')
        runner.run(discover)


if __name__ == '__main__':
    test_case = RunTestCase()
    test_case.main()
