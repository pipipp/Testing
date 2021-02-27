# -*- coding:utf-8 -*-
import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# logs根目录
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# test_case根目录
TEST_CASE_DIR = os.path.join(BASE_DIR, 'test_case')

# test_file根目录
TEST_FILE_DIR = os.path.join(BASE_DIR, 'test_file')

# result根目录
RESULT_DIR = os.path.join(BASE_DIR, 'result')


if __name__ == '__main__':
    print(BASE_DIR)
    print(LOGS_DIR)
    print(TEST_CASE_DIR)
    print(TEST_FILE_DIR)
    print(RESULT_DIR)
