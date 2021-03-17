# -*- coding:utf-8 -*-
""" ddt模块使用方法

@dd.ddt：
    装饰类。也就是装饰继承自TestCase的类

@ddt.data：
    装饰测试方法。参数是一系列的值

@ddt.file_data：
    装饰测试方法。参数是文件名，文件可以是json 或者 yaml类型

    注意，如果文件以".yml"或者".yaml"结尾，ddt会作为yaml类型处理，其他所有文件都会作为json文件处理

    如果文件中是列表，【每个列表的值会作为测试用例参数】，同时作为测试用例方法名后缀显示
    如果文件中是字典，字典的key会作为测试用例方法的后缀显示，【字典的值会作为测试用例参数】

@ddt.unpack：多个参数的时候使用
    传递的是复杂的数据结构时使用。比如使用元组或者列表，添加unpack之后，ddt会自动把元组或者列表对应到多个参数上

使用ddt后，测试用例方法名生成规则：
    会产生一个新的测试用例方法名：测试方法名_ordinal_data
        ordinal：整数，从1开始递增，表示加载次数
        data：对应的测试数据
"""
import unittest
from ddt import ddt, data, file_data, unpack


@ddt
class Demo(unittest.TestCase):

    @data(1, 2, 3)
    def test_a(self, value):  # 加载单个参数，共执行3次
        print('--------->test_a')
        print(value)

    @unpack
    @data(
        (4, 5, 6),
        (7, 8, 9)
    )
    def test_b(self, a, b, c):  # 加载多个参数，共执行2次
        print('--------->test_b')
        print(a, b, c)

    @file_data('demo.json')
    def test_c(self, value):  # 读取json文件
        print('--------->test_c')
        print(value)

    @file_data('demo.yaml')
    def test_d(self, value):  # 读取yaml文件
        print('--------->test_d')
        print(value)


if __name__ == '__main__':
    unittest.main(verbosity=2)
