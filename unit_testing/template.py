"""
unittest断言用法：
1. assertEqual(a, b, msg="Error info") 判断a,b是否相等，不相等时，抛出 msg
2. assertTure(x, msg="Error info") 判断x表达式是否为真，表达式为假时，抛出 msg
3. assertIn(a, b, msg="Error info") 判断a是否在b里面，a不在b里面时，抛出 msg
4. assertIsNone(x, msg="Error info") 判断x是否为空，x不为空时，抛出 msg
"""
import unittest

__author__ = 'Evan'


class MyClassTest(unittest.TestCase):

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

    def test_error_type(self):
        """测试异常类型，如果触发了指定的异常类型就为Pass"""
        with self.assertRaises(TypeError):
            self._add(1, [2])

    def test_add(self):
        """如果测试值和期待值相等就为Pass"""
        result = self._add(1, 2)
        self.assertEqual(result, 30, msg='这里填异常信息提示')


if __name__ == '__main__':
    unittest.main()
