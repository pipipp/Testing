# -*- coding:utf-8 -*-
import os

# 根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 项目目录
PROJECT_DIR = {
    'logs_dir': os.path.join(BASE_DIR, 'logs'),
    'test_case_dir': os.path.join(BASE_DIR, 'test_case'),
    'test_file_dir': os.path.join(BASE_DIR, 'test_file'),
    'result_dir': os.path.join(BASE_DIR, 'result'),
}

# 邮件配置
EMAIL = {
    'on_off': 'ON',
    'subject': '接口自动化测试报告',
    'app': 'Outlook',
    'addressee': 'evanliuu@qq.com',
    'cc': 'pipi@qq.com',
}
