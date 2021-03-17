# -*- coding:utf-8 -*-
""" Pytest模块使用方法

显示可用的内置函数参数：
    pytest --fixtures

显示收集到哪些测试用例：
    pytest --collect-only

Pytest Exit Code 含义：
    Exit code 0     所有用例执行完毕，全部通过
    Exit code 1     所有用例执行完毕，存在Failed的测试用例
    Exit code 2     用户中断了测试的执行
    Exit code 3     测试执行过程发生了内部错误
    Exit code 4     pytest 命令行使用错误
    Exit code 5     未采集到可用测试用例文件

用例执行：
    一、使用main函数执行方式：默认为当前目录以'test_'开头的文件和函数
        pytest.main(['-s', 'test_run.py'])  # 列表内第一个为执行参数，第二个为执行文件或目录

    二、使用命令执行方式：
        1. 在第N个用例失败后，结束测试执行
            pytest -x              # 第01次失败，就停止测试
            pytest --maxfail=2     # 出现2个失败就终止测试

        2. 指定测试文件
            pytest test_mod.py

        3. 指定测试目录
            pytest testing/

        4. 通过关键字表达式过滤执行：只运行名称匹配的测试方法
            pytest -k 'string expr'

        5. 通过 node id 指定测试用例（由模块文件名、分隔符、类名、分隔符、方法名、参数构成）
            运行模块中的指定用例：
                pytest test_mod.py::test_func
            运行模块中的指定方法：
                pytest test_mod.py::TestClass::test_method

        6. 通过标记表达式执行（执行被装饰器 @pytest.mark.slow 装饰的所有测试用例）
            pytest -m slow

        7. 通过导入包执行测试（这条命令会自动导入包 pkg.testing，并使用该包所在的目录，执行里面的用例）
            pytest --pyargs pkg.testing

        8. 多进程运行case：
            安装模块：pip install -U pytest-xdist
            运行模式：pytest test_example.py -n NUM  # NUM为并发的进程数

        9. 重试运行case：
            安装模块：pip install -U pytest-rerunfailures
            运行模式：pytest test_example.py --reruns NUM  # NUM为重试次数

        10. 显示print内容：
            运行模式：pytest test_example.py -s
            与多进程一起使用：pytest test_se.py -s -n 4

        11. 执行之前失败的用例
            失败的用例保存在 .pytest_cache 目录内：lastfailed
            使用命令：
                pytest --lf                        # --last-failed，只重新运行上次运行失败的用例（或如果没有失败的话会全部跑）
                pytest --ff                        # --failed-first，运行所有测试，但首先运行上次运行失败的测试
                pytest --nf                        # --new-first，根据文件插件的时间，新的测试用例会先运行
                pytest --cache-show=[CACHESHOW]    # 显示.pytest_cache文件内容，不会收集用例也不会测试用例，选项参数: glob (默认: '*')
                pytest --cache-clear               # 测试之前先清空.pytest_cache文件

    三、用例前置-后置用法：
        1. 方法级别 setup() / teardown()            # 在类里面，每个测试方法执行一次
        2. 类级别 setup_class() / teardown_class()  # 在类里面，只执行一次

高阶用法一：
    1. 使用fixture：用于预置处理或重复操作
        使用方法：
            @pytest.fixture(scope="function", params=None, autouse=False, ids=None, name=None)
        常用参数:
            scope：被标记方法的作用域
                1. function：        表示fixture函数在【每个测试方法执行前后】执行一次。优先于setup
                2. class：           表示fixture函数在【每个测试类执行前后】执行一次。优先于setup_class
                3. module：          表示fixture函数在【每个测试脚本执行前后】执行一次。
                4. package：         表示fixture函数在【测试包（文件夹）中【第一个测试用例】执行前和【最后一个测试用例】执行后】执行一次。
                5. session：         表示【所有测试的最开始和结束后】执行一次。
            params：提供参数数据，供调用函数使用，list类型
            autouse：是否自动运行（即使没有被任何地方调用），默认为False
            ids：测试用例的名称，将打印到测试结果中

    2. 跳过测试函数
        使用方法：默认False
            @pytest.mark.skipif(condition=2 > 1, reason="跳过该函数")

    3. 标记为预期失败函数：
        使用方法：默认False
            @pytest.mark.xfail(condition=2 > 1, reason="标注为预期失败")

    4. 函数数据参数化：方便测试函数对测试数据的获取，执行次数等于参数值数量
        使用方法：
             @pytest.mark.parametrize(argnames, argvalues, indirect=False, ids=None, scope=None)
        常用参数:
            argnames：   参数名，类型为字符串，对应调用函数的参数，多个参数用逗号隔开。例如：'a,b,c'
            argvalues：  参数对应值，类型为list，例如：[value]，多个的时候，[(value1, value2), (value1, value2)]
            ids：        测试用例的名称，将打印到测试结果中

高阶用法二：
    1. 修改 Python traceback 输出
        pytest --showlocals     # show local variables in tracebacks
        pytest -l               # show local variables (shortcut)
        pytest --tb=auto        # (default) 'long' tracebacks for the first and last
        pytest --tb=long        # exhaustive, informative traceback formatting
        pytest --tb=short       # shorter traceback format
        pytest --tb=line        # only one line per failure
        pytest --tb=native      # Python standard library formatting
        pytest --tb=no          # no traceback at all

    2. 执行失败的时候跳转到 PDB
        pytest --pdb                # 每次遇到失败都跳转到 PDB
        pytest -x --pdb             # 第一次遇到失败就跳转到 PDB，结束测试执行
        pytest --pdb --maxfail=3    # 只有前三次失败跳转到 PDB

    3. 设置断点
        在用例脚本中加入如下python代码，pytest会自动关闭执行输出的抓取
        在这里，其他test脚本不会受到影响，带断点的test上一个test正常输出
        用法：
             import pdb; pdb.set_trace()

    4. 获取用例执行性能数据
        获取最慢的10个用例的执行耗时
        用法：
            pytest --durations=10

    5. 生成 JUnitXML 格式的结果文件
        这种格式的结果文件可以被Jenkins或其他CI工具解析
        用法：
            pytest --junitxml=path

    6. 禁用插件
        例如：关闭 doctest 插件
        用法：
            pytest -p no:doctest

    7. 输出覆盖率的html报告
        使用命令：
            pytest -vv --cov=./ --cov-report=html
            open htmlcov/index.html
"""

import pytest


@pytest.fixture(params=[1, 2, 3])
def fixture_params(request):  # 传入参数request 获取params值
    return request.param  # 返回列表中每个值，直到为空，所以会执行多次


@pytest.fixture()
def before_outside():
    print('------->before in the outside')


# 通过装饰器加载类外部的fixture
@pytest.mark.usefixtures('before_outside')
class TestCase(object):

    def setup_class(self):
        """测试类加载前，执行一次"""
        print('------->setup_class')

    def teardown_class(self):
        """测试类加载后，执行一次"""
        print('------->teardown_class')

    def setup(self):
        """每个测试方法运行前，执行一次"""
        print('------->setup_method')

    def teardown(self):
        """每个测试方法运行后，执行一次"""
        print('------->teardown_method')

    @pytest.fixture()
    def before_class(self):
        print('------->before in the class')
        return 1

    def test_a(self, before_class):  # 通过参数方式加载fixture
        print('------->test_a')
        assert 1 == before_class, f'期待的值：{1}，实际的值：{before_class}'

    def test_b(self, fixture_params):  # 通过参数方式加载fixture
        print('------->test_b')
        assert 2 == fixture_params, f'期待的值：{2}，实际的值：{before_outside}'

    @pytest.mark.skipif(reason="跳过该函数")  # 跳过测试函数test_c
    def test_c(self):
        print('------->test_c')
        assert 0

    @pytest.mark.parametrize('a,b', [(1, 2), (3, 3)])  # 使用参数化传值
    def test_d(self, a, b):
        print('------->test_d')
        assert a == b


if __name__ == '__main__':
    pytest.main(['-s', 'test_run.py'])  # 调用pytest的main函数，指定执行'test_run.py'
    # pytest.main(['-s', 'test_run.py::TestCase::test_a'])  # 通过节点，指定执行test_a方法测试
