"""
使用Socket实现多主机之间的文件共享和实时同步
"""
import os
import time
import tqdm
import socket
import hashlib
import threading


class SocketFileSync(object):

    def __init__(self, local_host_ip, other_host_ip, file_directory='task'):
        """
        Socket初始化配置
        :param local_host_ip: 本地Server端IP和端口，元组类型：(ip, port)
        :param other_host_ip: 其他Server端IP和端口，列表类型：[(ip, port), (ip, port)]
        :param file_directory: 文件目录名
        """
        self.local_host_ip = local_host_ip
        self.other_host_ip = other_host_ip
        self.file_directory = file_directory

        self.file_location = os.path.join(os.getcwd(), file_directory)  # 文件目录绝对路径
        self.build_file_store()  # 创建文件存放目录

        self.waiting_time = 5  # 所有的time.sleep()时间
        self.socket_timeout_time = 10  # 服务端和客户端的Socket超时时间
        self.automatic_sync_time = 10  # 文件自动同步的等待时间

        self.maximum_transfer_size = 1073741824  # 文件传输上限1G
        self.buffer_size = 1024  # Socket buffer size
        self.latest_file_list = []  # 记录最新的文件列表，随着本地目录下的文件更改而更新
        self.socket_separator = '<SEP>'
        self.system_separator = '\\'

    def setup_server_side(self):
        """
        配置Server端Socket
        :return: server handle
        """
        server = socket.socket()  # 实例化Socket
        server.bind(self.local_host_ip)  # 绑定端口
        server.listen(5)  # 开始监听，并设置最大连接数为5
        ip, port = self.local_host_ip
        self.print_info(msg=f'服务端 {ip}:{port} 开启，等待客户端连接...')
        return server

    def setup_client_side(self, other_host):
        """
        配置Client端Socket
        :param other_host: 被连接的其他主机
        :return: client handle
        """
        ip, port = other_host
        client = socket.socket()  # 实例化Socket
        self.print_info(side='client', msg=f'开始连接服务端 {ip}:{port} ...')

        client.connect((ip, port))
        self.print_info(side='client', msg=f'连接服务端 {ip}:{port} 成功')
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
        with open(file_name, 'rb') as file:
            file_data = file.read()

        diff_check = hashlib.md5()
        diff_check.update(file_data)
        md5_code = diff_check.hexdigest()
        return md5_code

    @staticmethod
    def print_info(side='server', msg=''):
        """
        根据side打印不同的前缀信息
        :param side: 默认server端
        :param msg: 要打印的内容
        :return:
        """
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        if side == 'server':
            print(f'Server print >> {current_time} - {msg}')
        else:
            print(f'Client print >> {current_time} - {msg}')

    @staticmethod
    def send_socket_info(handle, msg, side='server', do_encode=True, do_print_info=True):
        """
        发送socket info，并根据side打印不同的前缀信息
        :param handle: socket句柄
        :param msg: 要发送的内容
        :param side: 默认server端
        :param do_encode: 是否需要encode，默认True
        :param do_print_info: 是否需要打印socket信息，默认True
        :return:
        """
        if do_encode:
            handle.send(msg.encode())
        else:
            handle.send(msg)

        if do_print_info:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            if side == 'server':
                print(f'Server send --> {current_time} - {msg}')
            else:
                print(f'Client send --> {current_time} - {msg}')

    def receive_socket_info(self, handle, expected_msg, side='server', do_decode=True, do_print_info=True):
        """
        循环接收socket info，判断其返回值，直到返回值出现为止，防止socket信息粘连，并根据side打印不同的前缀信息
        :param handle: socket句柄
        :param expected_msg: 期待接受的内容，如果接受内容不在返回结果中，一直循环等待，期待内容可以为字符串，也可以为多个字符串组成的列表或元组
        :param side: 默认server端
        :param do_decode: 是否需要decode，默认True
        :param do_print_info: 是否需要打印socket信息，默认True
        :return:
        """
        while True:
            if do_decode:
                socket_data = handle.recv(self.buffer_size).decode()
            else:
                socket_data = handle.recv(self.buffer_size)

            if do_print_info:
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                if side == 'server':
                    print(f'Server received ==> {current_time} - {socket_data}')
                else:
                    print(f'Client received ==> {current_time} - {socket_data}')

            # 如果expected_msg为空，跳出循环
            if not expected_msg:
                break

            if isinstance(expected_msg, (list, tuple)):
                flag = False
                for expect in expected_msg:  # 循环判断每个期待字符是否在返回结果中
                    if expect in socket_data:  # 如果有任意一个存在，跳出循环
                        flag = True
                        break
                if flag:
                    break
            else:
                if expected_msg in socket_data:
                    break
            time.sleep(self.waiting_time)
        return socket_data

    def get_local_all_file(self):
        """
        获取本地目录下所有的文件名、md5和size
        :return: file list
        [
            {'file': file_relative_path, 'md5': md5_value, 'size': size_value},
            {'file': file_relative_path, 'md5': md5_value, 'size': size_value},
            {'file': file_relative_path, 'md5': md5_value, 'size': size_value},
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
                    'file': self.file_directory + each_file.split(self.file_directory, 1)[-1],  # 截取相对路径
                    'md5': self.get_file_md5(file_name=each_file),
                    'size': os.path.getsize(each_file)
                })
            return file_list
        else:
            return []

    def start_server_forever_listen(self):
        """
        启动服务端永久监听，提供服务端和客户端的文件同步功能
        服务端事务：
            1. 提供本地目录下所有文件的信息给客户端
            2. 接收客户端传送过来的文件，并写入到本地目录
            3. 检查传送后的文件信息是否有误，如果有误实现重传功能
            4. 实时更新 self.latest_file_list 的值
        :return:
        """
        while True:
            server = None
            try:
                server = self.setup_server_side()  # 配置服务端
                conn, address = server.accept()
                conn.settimeout(self.socket_timeout_time)  # 设置服务端超时时间
                self.print_info(msg='当前连接客户端：{}'.format(address))

                # 与客户端握手
                self.receive_socket_info(handle=conn, expected_msg='客户端已就绪')
                self.send_socket_info(handle=conn, msg='服务端已就绪')

                self.receive_socket_info(handle=conn, expected_msg='请求服务端文件列表')
                all_file = self.get_local_all_file()
                if all_file:
                    # 发送服务端所有文件给客户端检查
                    self.send_socket_info(handle=conn, msg=str(all_file))
                else:
                    self.send_socket_info(handle=conn, msg='服务端没有任何数据')

                expect_info = ['不需要更新', '开始更新']
                socket_data = self.receive_socket_info(handle=conn, expected_msg=expect_info)

                # 如果不需要更新，跳到下次连接
                if expect_info[0] in socket_data:
                    continue

                self.send_socket_info(handle=conn, msg='服务端已收到更新请求')
                while True:
                    expect_info = ['全部更新完毕', '文件详情: ']
                    socket_data = self.receive_socket_info(handle=conn, expected_msg=expect_info)

                    # 如果全部更新完毕，跳出循环
                    if expect_info[0] in socket_data:
                        break

                    # 文件详情接收确认
                    file_name, file_size, file_md5 = socket_data.split(expect_info[1])[-1].split(self.socket_separator)
                    self.send_socket_info(handle=conn, msg='服务端已收到文件详情')

                    # TODO 判断文件是否在文件夹中，最后实现，单独加一个函数来处理
                    # files = file_name.split(self.system_separator)
                    # for each in files:  # 先拿到实际的文件名，只涉及一层，后续添加多个文件夹判断功能
                    #     if '.' in each:
                    #         file_name = each
                    #         break

                    # 接收客户端发送的文件，将二进制全部保存到python变量中
                    data_content = ''.encode()
                    while True:
                        socket_data = self.receive_socket_info(handle=conn, expected_msg='', do_decode=False)
                        if '文件传输完毕'.encode() in socket_data:
                            break
                        data_content += socket_data
                        self.send_socket_info(handle=conn, msg='服务端接收文件成功')

                    # 一次性写入文件，防止文件粘连
                    with open(file_name, 'wb') as wf:
                        wf.write(data_content)

                    # 检查文件传输后的size和md5
                    new_file_size = str(os.path.getsize(file_name))
                    new_file_md5 = self.get_file_md5(file_name=file_name)
                    if new_file_size != file_size or new_file_md5 != file_md5:
                        self.send_socket_info(handle=conn, msg='服务端写入文件有误，请重新传送...')
                    else:
                        self.send_socket_info(handle=conn, msg='服务端写入文件成功')

                server.close()
                time.sleep(self.waiting_time)

            except Exception as ex:
                self.print_info(msg='服务端发生错误: {}, 正在重新启动...'.format(ex))
                if server:
                    server.close()
                time.sleep(self.waiting_time)
            finally:
                # 每次服务端被请求后，更新最新的文件列表到self.latest_file_list
                self.latest_file_list = self.get_local_all_file()

    def check_local_file_status(self):
        """
        检查本地目录下的所有文件是否有变动，如果有变动跳出循环
        :return:
        """
        for _ in range(self.automatic_sync_time):
            all_file = self.get_local_all_file()
            if all_file:
                if all_file != self.latest_file_list:
                    break
            time.sleep(1)
        else:
            self.print_info(side='client', msg='到达同步时间，开始自动同步！')

    def start_client_request_file_sync(self):
        """
        启动客户端访问其他服务端请求文件同步
        触发机制:
            1. 当本地目录下有任一文件信息发生变动，如：文件名、文件大小、文件md5
            2. 添加或删除文件
            3. 每隔 self.automatic_sync_time 秒，自动请求同步一次
        :return:
        """
        while True:
            # 循环读取本地目录下的所有文件，判断是否启动客户端
            self.check_local_file_status()

            client = None
            try:
                # 启动客户端
                for each_host in self.other_host_ip:  # 循环连接每一个其他服务端请求文件同步
                    client = self.setup_client_side(each_host)  # 配置客户端
                    client.settimeout(self.socket_timeout_time)  # 设置客户端超时时间

                    # 与服务端握手
                    self.send_socket_info(handle=client, side='client', msg='客户端已就绪')
                    self.receive_socket_info(handle=client, side='client', expected_msg='服务端已就绪')

                    self.send_socket_info(handle=client, side='client', msg='请求服务端文件列表')
                    socket_data = self.receive_socket_info(handle=client, side='client', expected_msg='')

                    all_file = self.get_local_all_file()
                    if all_file:
                        if '服务端没有任何数据' in socket_data:
                            need_sync_files = all_file
                        else:
                            # 取出服务端所有的文件信息
                            server_file_mapping = {}
                            for server_file in eval(socket_data):  # 转变为字典格式，服务端文件名用作Key，方便读取
                                server_file_mapping[server_file['file']] = server_file

                            server_files = [i for i in server_file_mapping.keys()]  # 取出服务端所有的文件名

                            # 判断需要传输到服务端的文件
                            need_sync_files = []
                            for each_file in all_file:
                                if each_file['file'] not in server_files:  # 如果本地文件不在服务端，添加到同步文件中
                                    need_sync_files.append(each_file)
                                    continue

                                server_file_md5 = server_file_mapping[each_file['file']]['md5']
                                if each_file['md5'] != server_file_md5:  # 如果本地文件和服务端文件md5不同，添加到同步文件中
                                    need_sync_files.append(each_file)
                                    continue

                        if need_sync_files:
                            # 开始传输文件
                            self.send_socket_info(handle=client, side='client', msg='开始更新')
                            self.receive_socket_info(handle=client, side='client', expected_msg='服务端已收到更新请求')

                            for each_file in need_sync_files:  # 循环传输每一个文件
                                file_name = each_file['file']
                                file_size = each_file['size']
                                file_md5 = each_file['md5']

                                if file_size > self.maximum_transfer_size:
                                    self.print_info(side='client', msg=f'跳过超过文件传输上限的文件，'
                                                                       f'file：{file_name}，size：{file_size}')
                                    continue

                                while True:
                                    # 发送文件名、文件大小、md5值到服务端
                                    file_info = f'{file_name}{self.socket_separator}{file_size}{self.socket_separator}{file_md5}'
                                    self.send_socket_info(handle=client, side='client', msg=f'文件详情: {file_info}')
                                    self.receive_socket_info(handle=client, side='client', expected_msg='服务端已收到文件详情')

                                    # 发送文件内容到服务端，使用tqdm显示发送进度
                                    with tqdm.tqdm(desc=f'发送: {file_name}', total=file_size, unit='B', unit_divisor=1024) as bar:
                                        with open(file_name, 'rb') as rf:
                                            while True:
                                                # 读取文件
                                                bytes_read = rf.read(self.buffer_size)
                                                if not bytes_read:
                                                    break
                                                # 发送文件
                                                self.send_socket_info(handle=client, side='client',
                                                                      msg=bytes_read, do_encode=False, do_print_info=False)
                                                self.receive_socket_info(handle=client, side='client',
                                                                         expected_msg='服务端接收文件成功', do_print_info=False)
                                                bar.update(len(bytes_read))

                                    self.send_socket_info(handle=client, side='client', msg='文件传输完毕')

                                    # 确认文件传输后的size和md5
                                    socket_data = self.receive_socket_info(handle=client, side='client', expected_msg='')
                                    if '服务端写入文件有误' in socket_data:
                                        continue  # 如果服务端确认有误，retry
                                    break

                            self.send_socket_info(handle=client, side='client', msg='全部更新完毕')
                        else:
                            self.send_socket_info(handle=client, side='client', msg='不需要更新')
                    else:
                        self.send_socket_info(handle=client, side='client', msg='不需要更新')

                    client.close()
                    time.sleep(self.waiting_time)

            except Exception as ex:
                self.print_info(side='client', msg='客户端发生错误：{}'.format(ex))
                if client:
                    client.close()
                time.sleep(self.waiting_time)

    def main(self):
        # 记录本地目录下最初的所有文件，用于文件同步
        all_file = self.get_local_all_file()
        if all_file:
            self.latest_file_list = all_file

        threads = []
        # 配置所有线程
        start_server_forever_listen = threading.Thread(target=self.start_server_forever_listen)
        start_client_request_file_sync = threading.Thread(target=self.start_client_request_file_sync)

        # 添加所有线程到列表
        for t in [start_server_forever_listen, start_client_request_file_sync]:
            threads.append(t)

        # 开启所有线程
        for thread in threads:
            thread.start()


if __name__ == '__main__':
    file_sync = SocketFileSync(local_host_ip=('127.0.0.1', 6666),
                               other_host_ip=[('127.0.0.1', 9999)],
                               file_directory='task')
    file_sync.main()
