import os
import unittest
import HtmlTestRunner
from unit_testing.template.case.test_example import UnitTestExample

__author__ = 'Evan'


def run():
    """用例执行方案"""
    # 方案一
    unittest.main()  # 直接调用main方法启动所有以"test_"开头命名的方法，用例按照字母顺序执行

    # 方案二（使用suite套件，调用unittest类方法，自定义添加用例和执行顺序）
    suite = unittest.TestSuite()  # 实例化测试套件
    for each in ['test_case_3', 'test_case_1', 'test_case_2']:  # 按照加载顺序执行用例
        suite.addTest(UnitTestExample(each))
    runner = unittest.TextTestRunner()
    runner.run(suite)

    # 方案三（使用discover测试集，加载python文件启动所有用例）
    test_dir = os.path.join(os.path.dirname(__file__), 'case')  # 用例所在目录
    execute_python_file = 'test_*.py'  # 启动指定命名规则的python文件
    discover = unittest.defaultTestLoader.discover(start_dir=test_dir, pattern=execute_python_file)
    runner = unittest.TextTestRunner()
    runner.run(discover)


def generate_report():
    """使用HTMLTestRunner模块执行用例并生成HTML测试报告"""
    # 使用suite套件
    suite = unittest.TestSuite()
    for each in ['test_case_3', 'test_case_1', 'test_case_2']:
        suite.addTest(UnitTestExample(each))
    runner = HtmlTestRunner.HTMLTestRunner(output='./reports/', report_name='use_suite_reports')
    runner.run(suite)

    # 使用discover测试集
    test_dir = os.path.join(os.path.dirname(__file__), 'case')
    discover = unittest.defaultTestLoader.discover(start_dir=test_dir, pattern='test_*.py')
    runner = HtmlTestRunner.HTMLTestRunner(output='./reports/', report_name='use_discover_reports')
    runner.run(discover)


if __name__ == '__main__':
    run()
    # generate_report()
