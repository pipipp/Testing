# -*- coding:utf-8 -*-
"""
日志模块
"""

import os
import logging

from interface_testing.udts_api_test.settings import PROJECT_DIR
from logging.handlers import TimedRotatingFileHandler


class Logger(object):

    def __init__(self, logger_name=__name__):
        self.logger = logging.getLogger(logger_name)
        logging.root.setLevel(logging.NOTSET)
        self.log_file_name = 'logs.log'  # 日志文件的名称
        self.backup_count = 5  # 最多存放日志的数量
        # 日志输出级别
        self.console_output_level = 'WARNING'
        self.file_output_level = 'DEBUG'
        # 日志输出格式
        self.formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    def get_logger(self):
        """在logger中添加日志句柄并返回，如果logger已有句柄，则直接返回"""
        if not self.logger.handlers:  # 避免重复日志

            # 创建一个handler，用于输出到控制台
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self.formatter)
            console_handler.setLevel(self.console_output_level)
            self.logger.addHandler(console_handler)

            # 创建一个handler，用于写入日志文件（设置每天创建新的日志文件，最多保留backup_count份）
            file_handler = TimedRotatingFileHandler(filename=os.path.join(PROJECT_DIR['logs_dir'], self.log_file_name),
                                                    when='D', interval=1, backupCount=self.backup_count,
                                                    delay=True, encoding='utf-8')
            file_handler.setFormatter(self.formatter)
            file_handler.setLevel(self.file_output_level)
            self.logger.addHandler(file_handler)
        return self.logger


logger = Logger().get_logger()
