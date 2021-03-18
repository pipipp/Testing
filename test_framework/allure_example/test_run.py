# -*- coding:utf-8 -*-
""" Allure模块使用方法

特性：
    1. @allure.feature('info')               # 用于描述被测试产品需求
    2. @allure.story('info')                 # 用于描述feature的用户场景，即测试需求
    3. @pytest.allure.step('info')           # 用于将一些通用的函数作为测试步骤输出到报告，调用此函数的地方会向报告中输出步骤

    4. with allure.step('info')              # 用于描述测试步骤，将会输出到报告中
    5. allure.attach('info'，'期望结果')      # 用于向测试报告中输入一些附加的信息，通常是一些测试数据，截图等

生成Allure测试报告：
    一、生成测试报告数据
        1. pytest test_run.py --alluredir ./results/    # 执行所有用例，并生成报告到reports目录下
        2. pytest test_run.py --allure_features='aa' --allure_stories='bb'   # 执行指定的feature和story

    二、生成测试报告页面：--clean选项目的是先清空测试报告目录，再生成新的测试报告。
        allure generate ./results/ -o ./allure_reports/ --clean

Allure测试报告，常用页面介绍：
    1. Overview页面
        展示了本次测试的测试用例数量，成功用例、失败用例、跳过用例的比例，测试环境，SUITES，FEATURES BY STORIES等基本信息，
        当与Jenkins做了持续置成后，TREND区域还将显示，历次测试的通过情况。

    2. Behaviors页面
        这个页面按照 FEATURES 和 STORIES 展示测试用例的执行结果

    3. Suites页面
        将每一个测试脚本，作为一个Suite，可以看到所有脚本的测试情况

    4. Graphs页面
        这个页面展示了本次测试结果的统计信息，比如测试用例执行结果状态、测试用例重要等级分布、测试用例执行时间分布等。
"""

import pytest
import allure


@allure.feature('购物车功能')  # 用feature说明产品需求，可以理解为JIRA中的Epic
class TestShoppingTrolley(object):

    @allure.story('加入购物车')  # 用story说明用户场景，可以理解为JIRA中的Story
    def test_add_shopping_trolley(self):
        login('Evan', 'password')  # 步骤1，调用"step函数"

        with allure.step("浏览商品"):  # 步骤2，step的参数将会打印到测试报告中
            allure.attach('笔记本', '商品1')  # attach可以打印一些附加信息
            allure.attach('手机', '商品2')

        with allure.step("点击商品"):  # 步骤3
            pass

        with allure.step("校验结果"):  # 步骤4
            allure.attach('添加购物车成功', '期望结果')
            allure.attach('添加购物车失败', '实际结果')
            assert 'success' == 'failed'

    @allure.story('修改购物车')
    def test_edit_shopping_trolley(self):
        pass

    @pytest.mark.skipif(reason='本次不执行')
    @allure.story('删除购物车中商品')
    def test_delete_shopping_trolley(self):
        pass


@allure.step('用户登录')  # 将函数作为一个步骤，调用此函数时，报告中输出这个步骤，这样的函数叫"step函数"
def login(user, pwd):
    print(user, pwd)


if __name__ == '__main__':
    pytest.main(['-s'])
