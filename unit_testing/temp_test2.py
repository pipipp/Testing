"""
Client
"""
import socket
import tqdm
import os
import sys
import hashlib


def get_file_md5(fname):
    m = hashlib.md5()  # 创建md5对象
    with open(fname, 'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)  # 更新md5对象

    return m.hexdigest()  # 返回md5对象


# 遍历文件夹,返回文件名列表和对应md5
def walkFile(file):
    filelist = []
    md5list = []
    for root, dirs, files in os.walk(file):

        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list

        # 遍历文件
        for filename in files:
            filelist.append(os.path.join(root, filename))
            md5list.append(get_file_md5(os.path.join(root, filename)))

    return dict(zip(filelist, md5list))


cfiles = walkFile(os.getcwd())

# 传输数据的分隔符
SEPARATOR = "<SEP>"

# 服务器信息
host = "192.168.8.128"
port = 20001

# 文件传输的缓冲区
BUFFER_SIZE = 4096

# 传输文件的名字
# filename = "/root/桌面/python/ppt.rar"

# 文件大小
# filesize = os.path.getsize(filename)

# 创建socket连接

while True:
    s = socket.socket()

    # 连接服务器
    print(f"服务器连接中{host}:{port}")
    s.connect((host, port))
    print("服务器连接成功！")
    for key in cfiles:
        filename = key
        filesize = os.path.getsize(filename)
        filemd5 = cfiles[key]

        # 发送文件名字和文件大小，必须进行编码处理
        s.send(f"{filename}{SEPARATOR}{filesize}{SEPARATOR}{filemd5}".encode())

        # 文件传输
        progress = tqdm.tqdm(range(filesize), f"发送{filename}", unit="B", unit_divisor=1024)
        with open(filename, "rb") as f:
            for _ in progress:
                # 读取文件
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                # sendall确保网络忙碌时译然可以传输
                s.sendall(bytes_read)
                progress.update(len(bytes_read))

    s.close()