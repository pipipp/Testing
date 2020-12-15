"""
Server
"""
import socket
import os
import hashlib
import sys


def walkFile(file):
    filelist = []
    for root, dirs, files in os.walk(file):

        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list

        # 遍历文件
        for filename in files:
            filelist.append(os.path.join(root, filename))

    return filelist


server = socket.socket()
server.bind(('192.168.8.128', 30000))
server.listen()
print('等待客户端连接')

while True:
    conn, addr = server.accept()
    print('当前连接客户端：', addr)

    while True:
        files = walkFile(os.getcwd())
        filelist = ','.join(files)
        conn.send(filelist.encode())
        print('等待客户端下载指令')

        data = conn.recv(1024)
        if not data:
            print('客户端已断开连接')
            break
        filename = data.decode()
        if os.path.isfile(filename):  # 判断文件是否存在
            f = open(filename, 'rb')
            m = hashlib.md5()
            file_size = os.stat(filename).st_size  # 获取文件大小
            conn.send(str(file_size).encode())  # 发送文件大小
            conn.recv(1024)  # 等待确认
            for line in f:
                conn.send(line)  # 发送文件
                m.update(line)
            print("文件md5值：", m.hexdigest())
            conn.send(m.hexdigest().encode())  # 发送md5值
            f.close()
        print('发送完成')
server.close()
