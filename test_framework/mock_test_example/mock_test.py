import unittest
from unittest import mock


class SubClass(object):

    @staticmethod
    def add_func(a, b):
        """两个数相加"""
        return a + b


class TestSub(unittest.TestCase):
    """测试两个数相加"""

    def test_sub_mock(self):
        """
        使用mock测试
        :return:
        """
        sub = SubClass()  # 初始化被测函数类实例
        sub.add = mock.Mock(return_value=10)  # 使用mock，返回固定的值
        result = sub.add(5, 11)
        self.assertEqual(result, 16)

    def test_sub_actual(self):
        """
        使用真实的add_func测试
        :return:
        """
        sub = SubClass()  # 初始化被测函数类实例
        sub.add = mock.Mock(return_value=10,
                            side_effect=sub.add_func)  # 使用side_effect参数, 会覆盖return_value值
        result = sub.add(5, 11)
        self.assertEqual(result, 16)


if __name__ == '__main__':
    unittest.main()
