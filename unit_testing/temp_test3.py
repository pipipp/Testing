# -*- coding:utf-8 -*-
import time
import socket
import hashlib
import sys
import re
import os
import threading


INPUT_INFO = sys.argv
if len(INPUT_INFO) == 3:
    if INPUT_INFO[1] != '--ip':
        raise ValueError('The second parameter should be --ip')
    other_ip = INPUT_INFO[2]
else:
    raise ValueError('Parameter error, you must use command mode to start the program')
OTHER_IP = [(i, 5555) for i in other_ip.split(',')]

SERVER_IP = ('127.0.0.1', 3333)
# OTHER_IP = [('127.0.0.1', 5555)]

BUFFER_SIZE = 1024
MAXIMUM_SIZE = 1073741824
FILE_DIRECTORY = 'task'


def read_all_file():
    total_files = []
    for root, dirs, files in os.walk(FILE_DIRECTORY):
        for i in files:
            total_files.append(os.path.join(root, i))
    result = {}
    for index, file in enumerate(total_files, 1):
        result[str(index)] = {
            'filesize': os.path.getsize(file),
            'filepath': FILE_DIRECTORY + file.split(FILE_DIRECTORY, 1)[-1],
        }
    return result


def inspect_files(file):
    number = -1
    directory = []
    for i in range(len(file.split('\\')[:-1])-1):
        directory.append('\\'.join(file.split('\\')[:number]))
        number = number - 1
    for r in sorted(directory, reverse=True):
        if not os.path.isdir(r):
            os.mkdir(r)


def receive_server_data(sender, expected, need_decode=True):
    while True:
        if need_decode:
            server_data = sender.recv(BUFFER_SIZE).decode()
        else:
            server_data = sender.recv(BUFFER_SIZE)
        if expected is None:
            break
        if isinstance(expected, (list, tuple)):
            for expect in expected:
                if expect in server_data:
                    return
        else:
            if expected in server_data:
                break
        time.sleep(3)
    return server_data


def build_client_services():
    def _build_client_services():
        while True:
            client = None
            time.sleep(3)
            try:
                # 启动客户端
                for ips in OTHER_IP:  # 循环连接每一个其他服务端请求文件同步
                    client = socket.socket()  # 实例化Socket
                    client.connect(ips)
                    client.settimeout(10)

                    # 与服务端握手
                    client.send('client setup ok'.encode())
                    receive_server_data(sender=client, expected='server setup ok')

                    client.send('request server data'.encode())
                    server_data = receive_server_data(sender=client, expected=None)

                    total_file = read_all_file()
                    if total_file:
                        if 'no any data' in server_data:
                            transfer_files = total_file
                        else:
                            # 取出服务端所有的文件信息
                            server_files = {}
                            for key, value in eval(server_data).items():  # 转变为字典格式，服务端文件名用作Key，方便读取
                                server_files[value['filepath']] = value

                            # 判断需要传输到服务端的文件
                            transfer_files = []
                            for each_file in total_file.values():
                                if each_file['filepath'] not in server_files.keys():
                                    transfer_files.append(each_file)
                                    continue
                                if each_file['filesize'] != server_files[each_file['filepath']]['filesize']:
                                    transfer_files.append(each_file)
                                    continue

                        if transfer_files:
                            # 开始传输文件
                            client.send('start transfer files'.encode())
                            receive_server_data(sender=client, expected='received request')

                            for tf in transfer_files:  # 循环传输每一个文件
                                filepath = tf['filepath']
                                filesize = tf['filesize']

                                if filesize > MAXIMUM_SIZE:
                                    continue

                                while True:
                                    # 发送文件名、文件大小到服务端
                                    file_info = '{},{}'.format(filepath, filesize)
                                    client.send(file_info.encode())
                                    receive_server_data(sender=client, expected='received file detail info')

                                    # 发送文件内容到服务端
                                    with open(filepath, 'rb') as rf:
                                        while True:
                                            # 读取文件
                                            bytes_read = rf.read(BUFFER_SIZE)
                                            if not bytes_read:
                                                break
                                            # 发送文件
                                            client.send(bytes_read)
                                            result = receive_server_data(sender=client, expected='write ok')
                                            if 'write ok' in result:
                                                continue
                                            else:
                                                break

                                    client.send('file transfer done'.encode())

                            client.send('all transfer done'.encode())
                            print("all transfer done")
                        else:
                            client.send("Don't update".encode())
                            print("Don't update")
                    else:
                        client.send("Don't update".encode())
                        print("Don't update")

                    client.close()
                    time.sleep(3)

            except Exception as ex:
                print('Client encounters an error: {}'.format(ex))
                if client:
                    client.close()
                time.sleep(5)

    threading.Thread(target=_build_client_services).start()


def build_server_services():
    def _build_server_services():
        server = socket.socket()
        server.bind(SERVER_IP)
        server.listen()
        print('Start services {}, waiting for client connection......'.format(str(SERVER_IP)))

        while True:
            try:
                conn, addr = server.accept()
                conn.settimeout(10)
                print('Client {} accessed'.format(addr))

                # 与客户端握手
                receive_server_data(sender=conn, expected='client setup ok')
                conn.send('server setup ok'.encode())

                receive_server_data(sender=conn, expected='request server data')
                total_file = read_all_file()
                if total_file:
                    # 发送服务端所有文件给客户端检查
                    conn.send(str(total_file).encode())
                else:
                    conn.send('no any data'.encode())

                client_data = receive_server_data(sender=conn, expected=None)

                # 如果不需要更新，跳到下次连接
                if "Don't update" in client_data:
                    continue

                conn.send('received request'.encode())
                while True:
                    expect_info = ['全部更新完毕', '文件详情: ']
                    client_data = receive_server_data(sender=conn, expected=None)

                    # 如果全部更新完毕，跳出循环
                    if 'all transfer done' in client_data:
                        break

                    # 文件详情接收确认
                    filepath, filesize = client_data.split(',')
                    print('received filepath {}, filesize: {}'.format(filepath, filesize))
                    conn.send('received file detail info'.encode())

                    # 检查客户端传送过来的文件所处的文件夹是否存在，如果不存在创建一个新的
                    inspect_files(file=filepath)

                    # 接收客户端发送的文件，将二进制全部保存到python变量中
                    data = ''.encode()
                    while True:
                        result = conn.recv(BUFFER_SIZE)
                        if 'file transfer done'.encode() in result:
                            break
                        data += result
                        conn.send('file write ok'.encode())

                    # 写入文件
                    file_write = open(filepath, 'wb')
                    file_write.write(data)
                    file_write.close()
                    print('write {} successful'.format(filepath))

                time.sleep(3)

            except Exception as ex:
                print('Server encounters an error: {}'.format(ex))
                time.sleep(3)
    threading.Thread(target=_build_server_services).start()


def main():
    build_server_services()
    build_client_services()


if __name__ == '__main__':
    main()
