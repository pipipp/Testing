# -*- coding:utf-8 -*-
"""
接口压力测试
"""

import logging
import requests
import threading


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

save_log_path = 'test.log'
file_mode = 'a+'
format_info = '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'

# Add record logger function
fh = logging.FileHandler(save_log_path, mode=file_mode, encoding='utf-8')
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(format_info))
logger.addHandler(fh)
# Add display logger function
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter(format_info))
logger.addHandler(ch)


class StressTest(object):

    def __init__(self, url='', params={}, headers={}, thread_sum=100):
        """
        初始化请求配置
        :param url: 请求URL
        :param params: 请求参数
        :param headers: 请求头
        :param thread_sum: 线程并发数（压力次数）
        """
        self.url = url
        self.params = params
        self.headers = headers
        self.thread_sum = thread_sum

        self.session = requests.session()
        self.session.headers.update(headers)

        self.request_time = []
        self.pass_count = 0
        self.fail_count = 0

    def set_cookies(self, raw_cookies=''):
        """
        设置cookies
        :param raw_cookies: 浏览器上保存下来的cookies
        :return:
        """
        cookies = {}
        for line in raw_cookies.split(';'):
            name, value = line.strip().split('=', 1)
            cookies[name] = value
        self.session.cookies.update(cookies)
        logger.debug('添加cookies...')

    def request_test(self, number):
        """
        请求测试
        :param number: 线程号
        :return:
        """
        try:
            resp = self.session.get(self.url, params=self.params)
            self.request_time.append(resp.elapsed.total_seconds())  # 保存请求时长（秒）

            if resp.status_code == 200:
                self.pass_count += 1
                # logger.debug(f'第（{number}）次请求成功！')
            else:
                self.fail_count += 1
                logger.warning(f'第（{number}）次请求失败，状态码：{resp.status_code}')
        except Exception as ex:
            self.fail_count += 1
            logger.warning(f'第（{number}）次请求失败，错误信息：{ex}')

    def summary(self):
        """压测结果总结"""
        logger.debug('请求配置' + '*' * 50)
        logger.debug(f'url：{self.url}')
        logger.debug(f'params：{self.params}')
        logger.debug(f'headers：{self.headers}')
        logger.debug(f'thread_sum：{self.thread_sum}')
        logger.debug('*' * 58)

        logger.info(f'压测次数：{self.thread_sum}')
        logger.info(f'请求通过次数：{self.pass_count}')
        logger.info(f'请求异常次数：{self.fail_count}')

        max_time = float('{:.2f}'.format(max(self.request_time) * 1000))  # 转换为毫秒
        min_time = float('{:.2f}'.format(min(self.request_time) * 1000))  # 转换为毫秒
        logger.info(f'总响应最大时长：{max_time}ms')
        logger.info(f'总响应最小时长：{min_time}ms')

        avg_time = float('{:.2f}'.format((sum(self.request_time) / len(self.request_time) * 1000)))  # 转换为毫秒
        tps = float('{:.2f}'.format(self.thread_sum / (avg_time / 1000)))  # 转换为秒，并发数/平均响应时长
        logger.info(f'平均响应时长：{avg_time}ms')
        logger.info(f'TPS（并发数/平均响应时长）：{tps}/s')

    def main(self):
        threads = []
        for number in range(1, self.thread_sum + 1):
            t = threading.Thread(target=self.request_test, args=(number, ))
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.summary()


if __name__ == '__main__':
    test = StressTest(
        url='http://127.0.0.1:8000/proxy/',
        params={
            'about': 'all'
        },
        headers={},
        thread_sum=600,
    )
    test.main()
