"""
使用Socket实现多主机之间的文件共享
"""
import os
import time
import socket
import hashlib
import threading

from tqdm import tqdm


class SocketFileSharing(object):

    def __init__(self, other_host_ip, local_host_ip=('127.0.0.1', 9999), file_directory='task'):
        self.other_host_ip = other_host_ip  # 其他Server端IP和端口
        self.local_host_ip = local_host_ip  # 本地Server端IP和端口

        self.file_location = os.path.join(os.getcwd(), file_directory)  # 文件目录绝对路径
        self.build_file_store()  # 创建文件存放目录

        self.server_in_progress = False  # 判断Server是否正在交互中
        self.client_in_progress = False  # 判断Client是否正在交互中
        self.buffer_size = 1024

    def setup_server_side(self):
        """
        配置Server端Socket
        :return: server handle
        """
        server = socket.socket()  # 实例化Socket
        server.bind(self.local_host_ip)  # 绑定端口
        server.listen(5)  # 开始监听，并设置最大连接数为5
        ip, port = self.local_host_ip
        self.print_info(msg=f'服务器端 {ip}:{port} 开启，等待客户端连接...')
        return server

    def setup_client_side(self, other_host):
        """
        配置Client端Socket
        :param other_host: 被连接的其他主机
        :return: client handle
        """
        ip, port = other_host
        client = socket.socket()  # 实例化Socket
        self.print_info(side='client', msg=f'开始连接服务器 {ip}:{port} ...')

        client.connect((ip, port))
        self.print_info(side='client', msg=f'连接服务器 {ip}:{port} 成功')
        return client

    def build_file_store(self):
        """
        创建文件存放目录
        :return:
        """
        if not os.path.isdir(self.file_location):
            os.mkdir(self.file_location)

    @staticmethod
    def get_file_md5(file_name=''):
        """
        获取文件的MD5值
        :param file_name: 被读取的文件
        :return: md5 string
        """
        with open(file_name, 'r', encoding='utf-8') as file:
            file_data = file.read()

        diff_check = hashlib.md5()
        diff_check.update(file_data.encode())
        md5_code = diff_check.hexdigest()
        return md5_code

    @staticmethod
    def print_info(side='server', msg=''):
        """
        根据side添加不同的前缀信息
        :param side:
        :param msg:
        :return:
        """
        if side == 'server':
            print(f'Server msg --> {msg}')
        else:
            print(f'Client msg --> {msg}')

    def get_local_all_file(self):
        """
        获取本地目录下所有文件的md5和size
        :return: file list
        [
            {'file': file_name_1, 'md5': md5_value, 'size': size_value},
            {'file': file_name_2, 'md5': md5_value, 'size': size_value},
            {'file': file_name_3, 'md5': md5_value, 'size': size_value},
            ...
        ]
        """
        all_files = []
        for root, dirs, files in os.walk(self.file_location):  # 展开文件目录下所有的子目录和文件
            # root 返回一个当前文件夹的绝对路径 - str
            # dirs 返回该文件夹下所有的子目录名 - list
            # files 返回该文件夹下所有的子文件 - list
            for each_file in files:  # 遍历保存所有的文件
                all_files.append(os.path.join(root, each_file))

        if all_files:
            file_list = []
            for each_file in all_files:  # 如果本地目录有文件，循环读取每一个文件名的md5和文件大小
                file_list.append({
                    'file': each_file,
                    'md5': self.get_file_md5(file_name=each_file),
                    'size': os.path.getsize(each_file)
                })
            return file_list
        else:
            return []

    def start_server_forever_listen(self):
        """
        启动服务器端永久监听
        :return:
        """
        server = self.setup_server_side()  # 配置Server端
        while True:
            try:
                conn, address = server.accept()
                self.print_info(msg='当前连接客户端：{}'.format(address))

                if self.client_in_progress:  # 如果当前客户端正在访问其他服务器，阻塞服务器端交互，保持文件同步
                    conn.send('目标服务器正在与其他服务器同步，请稍等...'.encode())
                    continue

                self.server_in_progress = True
                all_file = self.get_local_all_file()
                if all_file:
                    conn.send(str(all_file).encode())  # 发送服务器端所有文件给客户端检查
                else:
                    conn.send('目标服务器没有任何数据'.encode())

                while True:
                    socket_data = conn.recv(self.buffer_size).decode()
                    if socket_data:
                        self.print_info(msg=f'{address} {socket_data}')

                        if '不需要更新' in socket_data or '更新已完成' in socket_data:
                            break

                        if '需要同步的文件' in socket_data:
                            need_update_files = socket_data
                            # with open('')

            except Exception as ex:
                self.print_info(msg='服务器端发生错误：{}, 正在重新启动...'.format(ex))
                if server:
                    server.close()
                time.sleep(1)
                self.server_in_progress = False

    def start_client_request_file_sync(self):
        """
        启动客户端间隔访问每个其他服务器请求文件同步
        :return:
        """
        while True:
            client = None
            for each_host in self.other_host_ip:  # 循环连接每一个其他服务器

                while self.server_in_progress:  # 如果当前服务器端被其他客户端访问，阻塞客户端访问其他服务器，保持文件同步
                    time.sleep(5)  # 每5秒检查一次状态
                    continue

                try:
                    client = self.setup_client_side(each_host)  # 配置Client访问指定的Server端
                    while True:
                        socket_data = client.recv(self.buffer_size).decode()
                        if '目标服务器正在与其他服务器同步' in socket_data:
                            self.print_info(side='client', msg=socket_data)
                            continue
                        break

                    all_file = self.get_local_all_file()
                    if all_file:
                        if '目标服务器没有任何数据' in socket_data:
                            self.print_info(side='client', msg=socket_data)
                            client.send(f'需要同步的文件：{all_file}'.encode())
                        else:
                            self.print_info(side='client', msg=f'服务器端文件：{socket_data}')
                            # 计算本地目录下的文件和服务器端文件的不同
                            need_sync_files = []
                            server_all_file = [i['file'] for i in eval(socket_data)]  # 取出服务器端所有的文件名
                            for each_file in all_file:
                                if each_file['file'] not in server_all_file:
                                    need_sync_files.append(each_file)

                            if need_sync_files:
                                client.send(f'需要同步的文件：{need_sync_files}'.encode())
                            else:
                                client.send('不需要更新'.encode())
                    else:
                        client.send('不需要更新'.encode())
                    client.close()

                except Exception as ex:
                    self.print_info(side='client', msg='客户端发生错误：{}'.format(ex))
                    if client:
                        client.close()
                    time.sleep(1)

    def main(self):
        threads = []
        # 配置所有线程
        start_server_forever_listen = threading.Thread(target=self.start_server_forever_listen)
        start_client_request_file_sync = threading.Thread(target=self.start_client_request_file_sync)

        # 添加所有事件到列表
        for t in [start_server_forever_listen, start_client_request_file_sync]:
            threads.append(t)

        # 开启所有线程
        for thread in threads:
            thread.start()


if __name__ == '__main__':
    file_sharing = SocketFileSharing(other_host_ip=[('127.0.0.1', 6666)],
                                     local_host_ip=('127.0.0.1', 9999),
                                     file_directory='task')
    file_sharing.main()
