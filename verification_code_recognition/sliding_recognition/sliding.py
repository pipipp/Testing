# -*- coding:utf-8 -*-
"""
滑动验证码识别

思路：
    一、获取滑动验证码背景图
        1. 使用Selenium模拟点击验证按钮
        2. 保存滑动验证码背景图的坐标：左上右下
        3. 截取整个页面，根据坐标裁剪出滑动验证码背景图
        4. 执行JS将原始背景图显示出来（将canvas节点的style设为空），再次执行2-3步骤
        5. 此时获得两张背景图，有缺口的 + 原始图

    二、模拟拖动
        1. 对比两个图片，获取缺口偏移量
        2. 获取滑动验证码对象
        3. 滑动滑块到缺口处（为防止被识别为程序操作，可增加拖动次数模拟人的行为，如：模拟滑动超出15像素后，再往回滑动）
"""

import time

from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SlidingRecognition(object):

    def __init__(self):
        self.url = 'https://www.geetest.com/demo/slide-popup.html'
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")  # 最大化窗口
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 30)

    def login(self):
        self.browser.get(self.url)

    def click_slider_button(self):
        """
        点击按钮，弹出滑动验证码
        :return:
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
        button.click()

    def get_sliding_position(self):
        """
        获取验证码背景图的坐标位置
        :return: 返回左上右下四个值。左上，右下分别是图片左上角和图片右下角的坐标
        """
        image = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_bg')))
        location = image.location
        size = image.size
        left, upper = location['x'], location['y']
        right, lower = location['x'] + size['width'], location['y'] + size['height']
        return left, upper, right, lower

    def get_page_screenshot(self):
        """
        获取网页全屏截图
        :return:
        """
        page_screenshot = self.browser.get_screenshot_as_png()
        page_screenshot = Image.open(BytesIO(page_screenshot))
        return page_screenshot

    def get_sliding_picture(self, picture_name):
        """
        保存滑动验证码图片
        :param picture_name: 保存图片的名称
        :return: 图片对象
        """
        left, upper, right, lower = self.get_sliding_position()  # 获取验证码背景图的左上、右下坐标
        page_screenshot = self.get_page_screenshot()  # 获取网页全屏截图
        sliding_img = page_screenshot.crop((left, upper, right, lower))  # 使用crop方法裁剪图片
        sliding_img.save(picture_name)  # 保存裁剪后的滑动验证码背景图到本地
        return sliding_img

    def hide_slider(self):
        """
        执行JS代码，隐藏滑块，展现完整的滑动验证码背景图
        :return:
        """
        # 将滑块隐藏
        # js = 'document.getElementsByClassName("geetest_canvas_slice geetest_absolute")[0].style="display:none;"'

        # 将滑块的节点style设为空，展现出原本的背景图
        js = 'document.querySelectorAll("canvas")[2].style=""'
        self.browser.execute_script(js)

    @staticmethod
    def is_pixel_equal(gap_img, raw_img, x, y):
        """
        判断两个像素是否相同
        :param gap_img: 有缺口的背景图对象
        :param raw_img: 原始图对象
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 获取图片指定位置的像素点
        pixel1 = gap_img.load()[x, y]
        pixel2 = raw_img.load()[x, y]
        threshold = 50  # 设定阈值
        # 对比两张图片的像素值，找出差距过大的位置
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold and abs(pixel1[3] - pixel2[3]) < threshold:
            return True
        else:
            return False

    def get_gap(self, gap_img, raw_img):
        """
        对比两个图片，获取缺口偏移量
        :param gap_img: 有缺口的背景图对象
        :param raw_img: 原始图对象
        :return: 缺口偏移量
        """
        left = 60
        # 先假定滑块的left位置为60，然后从右侧开始往后找，直到像素点不同就停止，这个就是缺口的位置
        for i in range(left, gap_img.size[0]):
            for j in range(raw_img.size[1]):
                if not self.is_pixel_equal(gap_img, raw_img, i, j):
                    left = i
                    return left
        return left

    @staticmethod
    def get_track(distance):
        """
        根据偏移量获取移动轨迹

        利用两个公式构造轨迹移动算法:
            x = v0 * t + 0.5 * a * t * t
            y = v0 + a * t

        :param distance: 缺口偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 2
            else:
                # 加速度为负3
                a = -3
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def get_back_track(self):
        """
        模拟滑动超出15像素后的往回滑动
        :return:
        """
        tracks = [-1, -1, -1, -2, -2, -3, -2, -2, -1]
        for x in tracks:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.1)

    def mouse_shake(self):
        """
        模拟释放鼠标手抖了一个机灵
        :return:
        """
        ActionChains(self.browser).move_by_offset(xoffset=3, yoffset=0).perform()
        ActionChains(self.browser).move_by_offset(xoffset=-3, yoffset=0).perform()
        time.sleep(0.2)

    def get_slider(self):
        """
        获取滑动验证码对象
        :return:
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        return slider

    def move_slider(self, slider, track):
        """
        滑动滑块到缺口处
        :param slider: 滑块位置
        :param track: 滑动轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()

        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()  # 执行鼠标滑动
        time.sleep(0.5)

        # self.get_back_track()  # 模拟滑动超出15像素后的往回滑动
        self.mouse_shake()  # 模拟释放鼠标手抖了一个机灵

        ActionChains(self.browser).release().perform()  # 执行鼠标松开

    def main(self):
        while True:
            try:
                self.login()
                self.click_slider_button()  # 点击验证按钮

                # 获取滑动验证码背景图
                gap_img = self.get_sliding_picture(picture_name='gap.png')  # 得到有缺口的背景图
                self.hide_slider()  # 执行JS，隐藏滑块缺口
                raw_img = self.get_sliding_picture(picture_name='raw.png')  # 得到原始图

                # 模拟拖动
                gap_distance = self.get_gap(gap_img, raw_img)  # 对比两个图片，获取缺口偏移量
                gap_distance -= 6  # 减去缺口位移

                track = self.get_track(gap_distance)  # 根据偏移量获取移动轨迹

                slider = self.get_slider()  # 获取滑动验证码对象
                self.move_slider(slider, track)  # 滑动滑块到缺口处

                # 点击登陆
                result = self.wait.until(
                    EC.text_to_be_present_in_element((By.CLASS_NAME, 'geetest_success_radar_tip_content'), '验证成功'))
                print('登录情况：', result)
                break

            except Exception as ex:
                print(f'Login failed, error msg: {ex}')
                print('try again!!!')
                self.main()


if __name__ == '__main__':
    sliding = SlidingRecognition()
    sliding.main()
