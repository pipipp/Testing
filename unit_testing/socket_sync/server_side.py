import socket
from tool import *


def setup_server_side(ip, port):
    server = socket.socket()
    server.bind((ip, port))
    server.listen()
    print(f'Start server {ip}:{port}, waiting for client connection......')
    return server


def start_server_services(ip):
    def _start_server_services():
        while True:
            conn, address = server.accept()
            conn.settimeout(SOCKET_TIMEOUT)
            print('当前连接客户端：{}'.format(address))

            # 与客户端达成一致
            receive_socket_data(handle=conn, expected='客户端已就绪')
            conn.send('服务端已就绪'.encode())

            receive_socket_data(handle=conn, expected='请求服务端文件列表')
            all_file = get_local_all_file()
            if all_file:
                # 发送服务端所有文件给客户端检查
                conn.send(str(all_file).encode())
            else:
                conn.send('服务端没有任何数据'.encode())

            expect_info = ['不需要更新', '开始更新']
            socket_data = receive_socket_data(handle=conn, expected=expect_info)

            # 如果不需要更新，跳到下次连接
            if expect_info[0] in socket_data:
                print('客户端不需要更新')
                continue

            conn.send('服务端已收到更新请求'.encode())
            while True:
                expect_info = ['全部更新完毕', '文件详情: ']
                socket_data = receive_socket_data(handle=conn, expected=expect_info)

                # 如果全部更新完毕，跳出循环
                if expect_info[0] in socket_data:
                    break

                # 文件详情接收确认
                file_name, file_size, file_md5 = socket_data.split(expect_info[1])[-1].split(SOCKET_SEPARATOR)
                print(f'服务端已收到文件详情：{file_name}，{file_size}，{file_md5}')
                conn.send('服务端已收到文件详情'.encode())

                # 检查客户端传送过来的文件所处的文件夹是否存在，如果不存在创建一个新的
                check_transfer_folder_exists(files=file_name)

                print('服务端开始接受文件...')
                # 接收客户端发送的文件，将二进制全部保存到python变量中
                data_content = ''.encode()
                while True:
                    socket_data = receive_socket_data(handle=conn, expected='', need_decode=False)
                    if '文件传输完毕'.encode() in socket_data:
                        break
                    data_content += socket_data
                    conn.send('服务端接收文件成功'.encode())

                print(f'文件-[{file_name}]接受成功，开始写入文件...')
                # 一次性写入文件，防止文件粘连
                with open(file_name, 'wb') as wf:
                    wf.write(data_content)

                # 检查文件传输后的size和md5
                new_file_size = str(os.path.getsize(file_name))
                new_file_md5 = get_file_md5(file_name=file_name)
                if new_file_size != file_size or new_file_md5 != file_md5:
                    conn.send('服务端写入文件有误，请重新传送...'.encode())
                else:
                    conn.send('服务端写入文件成功'.encode())
            time.sleep(5)

    server = setup_server_side(ip, SERVER_PORT)
    while True:
        try:
            _start_server_services()
        except Exception as ex:
            print('Server encounters an error: {}'.format(ex))
            time.sleep(2)
