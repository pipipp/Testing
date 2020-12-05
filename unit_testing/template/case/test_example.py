"""
unittest常用断言方法：
1. assertEqual(a, b, msg="Error info") 判断a,b是否相等，不相等时，抛出 msg
2. assertTure(x, msg="Error info") 判断x表达式是否为真，表达式为假时，抛出 msg
3. assertIn(a, b, msg="Error info") 判断a是否在b里面，a不在b里面时，抛出 msg
4. assertIsNone(x, msg="Error info") 判断x是否为空，x不为空时，抛出 msg
"""
import unittest

__author__ = 'Evan'


class UnitTestExample(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """在执行所有测试之前执行一次，用于做项目的初始化动作"""
        print("**********Test Start**********")

    @classmethod
    def tearDownClass(cls):
        """在执行完所有测试之后执行一次，用于做项目的收尾动作"""
        print('**********Test Done**********')

    def setUp(self):
        """在每个测试方法之前执行"""
        print('setUp...')

    def tearDown(self):
        """在每个测试方法之后执行"""
        print('tearDown...')

    @staticmethod
    def _add(a, b):
        return a + b

    @staticmethod
    def _sub(a, b):
        return a - b

    def test_case_1(self):
        """测试异常类型，如果触发了指定的异常类型就为Pass"""
        with self.assertRaises(TypeError):
            self._add(1, [2])

    @unittest.skip('skip the case test for test_case_2')
    def test_case_2(self, a=1, b=2, expect_value=30):
        """
        计算两个值相加，如果测试值和期待值相等就为Pass
        :param a:
        :param b:
        :param expect_value:
        :return:
        """
        result = self._add(a, b)
        self.assertEqual(result, expect_value, msg=f'Failed message: {a} + {b} != {expect_value}')

    def test_case_3(self, a=7, b=2, expect_value=50):
        """
        计算两个值相减，如果测试值和期待值相等就为Pass
        :param a:
        :param b:
        :param expect_value:
        :return:
        """
        result = self._sub(a, b)
        self.assertEqual(result, expect_value, msg=f'Failed message: {a} - {b} != {expect_value}')
