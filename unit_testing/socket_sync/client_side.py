import tqdm
import socket
from tool import *


def setup_client_side(ip, port):
    client = socket.socket()
    client.connect((ip, port))
    print(f'connect {ip}:{port} successful')
    return client


def start_client_side(all_remote_ip):
    def _start_client_side():
        while True:
            time.sleep(3)
            for remote_ip in all_remote_ip:
                ip, port = remote_ip, CLIENT_PORT
                client = setup_client_side(ip, port)
                client.settimeout(SOCKET_TIMEOUT)

                # 与服务端达成一致
                client.send('客户端已就绪'.encode())
                receive_socket_data(handle=client, expected='服务端已就绪')

                client.send('请求服务端文件列表'.encode())
                socket_data = receive_socket_data(handle=client, expected='')

                all_file = get_local_all_file()
                if all_file:
                    if '服务端没有任何数据' in socket_data:
                        need_sync_files = all_file
                    else:
                        # 取出服务端所有的文件信息
                        server_file_mapping = {}
                        for server_file in eval(socket_data):
                            server_file_mapping[server_file['file']] = server_file

                        # 判断需要传输到服务端的文件
                        need_sync_files = []
                        for each_file in all_file:
                            if each_file['file'] not in server_file_mapping:
                                need_sync_files.append(each_file)
                                continue
                            server_file_md5 = server_file_mapping[each_file['file']]['md5']
                            if each_file['md5'] != server_file_md5:
                                need_sync_files.append(each_file)
                                continue

                    if need_sync_files:
                        client.send('开始更新'.encode())
                        receive_socket_data(handle=client, expected='服务端已收到更新请求')

                        for each_file in need_sync_files:  # 循环传输每一个文件
                            file_name, file_size, file_md5 = each_file['file'], each_file['size'], each_file['md5']
                            if file_size > MAXIMUM_TRANSFER_SIZE:
                                continue
                            while True:
                                # 发送文件名、文件大小、md5值到服务端
                                file_info = f'{file_name}{SOCKET_SEPARATOR}{file_size}{SOCKET_SEPARATOR}{file_md5}'
                                client.send(f'文件详情: {file_info}'.encode())
                                print(f'发送文件详细信息到服务端：{file_info}')
                                receive_socket_data(handle=client, expected='服务端已收到文件详情')

                                print('客户端开始发送文件...')
                                # 发送文件内容到服务端
                                with tqdm.tqdm(desc=f'发送: {file_name}', total=file_size, unit='B',
                                               unit_divisor=1024) as bar:
                                    with open(file_name, 'rb') as rf:
                                        while True:
                                            # 读取文件
                                            bytes_read = rf.read(BUFFER_SIZE)
                                            if not bytes_read:
                                                break
                                            # 发送文件
                                            client.send(bytes_read)
                                            receive_socket_data(handle=client, expected='服务端接收文件成功')
                                            bar.update(len(bytes_read))

                                client.send('文件传输完毕'.encode())

                                # 确认文件传输后的size和md5
                                socket_data = receive_socket_data(handle=client, expected='')
                                if '服务端写入文件有误' not in socket_data:
                                    break

                        client.send('全部更新完毕'.encode())
                        print('客户端全部更新完毕')
                    else:
                        client.send('不需要更新'.encode())
                        print('客户端不需要更新')
                else:
                    client.send('不需要更新'.encode())
                    print('客户端不需要更新')

                client.close()
                time.sleep(5)
    while True:
        try:
            _start_client_side()
        except Exception as ex:
            print('Client encounters an error: {}'.format(ex))
