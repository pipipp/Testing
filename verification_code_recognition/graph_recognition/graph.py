# -*- coding:utf-8 -*-
"""
图形验证码识别
"""

import tesserocr
from PIL import Image


def graph_recognition(picture, threshold=150):
    """
    图形验证码识别
    :param picture: 图片路径
    :param threshold: 指定二值化的阈值，此值会影响处理后的图片清晰度
    :return:
    """
    image = Image.open(picture)

    # 将图片转化为灰度图像
    image = image.convert('L')
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    image = image.point(table, '1')  # 二值化处理
    # image.show()  # 显示处理后的图片

    result = tesserocr.image_to_text(image)  # 识别图片，转化为字符串，如果没结果，调整阈值大小
    return result


if __name__ == '__main__':
    code = graph_recognition(picture='demo.jpg')
    print(f'图形验证码识别：{code}')
