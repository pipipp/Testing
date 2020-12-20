import re
import os
import time
import hashlib
from config import *


def create_directory(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)


def get_file_md5(file_name=''):
    with open(file_name, 'rb') as file:
        file_data = file.read()

    diff_check = hashlib.md5()
    diff_check.update(file_data)
    md5_code = diff_check.hexdigest()
    return md5_code


def receive_socket_data(handle, expected, need_decode=True):
    """解决Socket粘包问题"""
    while True:
        if need_decode:
            data = handle.recv(BUFFER_SIZE).decode()
        else:
            data = handle.recv(BUFFER_SIZE)
        if not expected:
            break
        if isinstance(expected, (list, tuple)):
            break_flag = False
            for expect in expected:
                if expect in data:
                    break_flag = True
                    break
            if break_flag:
                break
        else:
            if expected in data:
                break
        time.sleep(3)
    return data


def get_local_all_file():
    """获取本地目录下所有的文件名、md5和size"""
    all_files = []
    for root, dirs, files in os.walk(DIRECTORY):  # 展开文件目录下所有的子目录和文件
        # root 返回一个当前文件夹的绝对路径 - str
        # dirs 返回该文件夹下所有的子目录名 - list
        # files 返回该文件夹下所有的子文件 - list
        for each_file in files:  # 遍历保存所有的文件
            all_files.append(os.path.join(root, each_file))

    if all_files:
        file_list = []
        for each_file in all_files:  # 如果本地目录有文件，循环读取每一个文件名的md5和文件大小
            file_list.append({
                'file': DIRECTORY + each_file.split(DIRECTORY, 1)[-1],  # 截取相对路径
                'md5': get_file_md5(file_name=each_file),
                'size': os.path.getsize(each_file)
            })
        print(f'本地目录所有文件：{file_list}')
        return file_list
    else:
        return []


def check_transfer_folder_exists(files):
    """
    检查客户端传送过来的文件夹是否存在，如果不存在创建一个新的
    :param files:
    :return:
    """
    split_folders = files.split(SYSTEM_SEPARATOR)
    folders = split_folders[:-1]
    split_number = -1
    check_folder_list = []
    for _ in range(len(folders) - 1):
        check_folder_list.append(SYSTEM_SEPARATOR.join(split_folders[:split_number]))
        split_number -= 1
    check_folder_list.reverse()
    for each_folder in check_folder_list:
        if not os.path.isdir(each_folder):
            os.mkdir(each_folder)


def get_local_ip():
    info = os.popen('ifconfig').read()
    result = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', info)
    if result:
        local_ip = result.group(1)
    else:
        raise ValueError('抓取本地主机IP失败')
    return local_ip
