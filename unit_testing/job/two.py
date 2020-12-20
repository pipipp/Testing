import threading
import re
import hashlib
import tqdm
import os
import sys
import time
import socket

INPUT_INFO = sys.argv
if len(INPUT_INFO) == 3:
    if INPUT_INFO[1] != '--ip':
        raise ValueError('The second parameter should be --ip')
    other_ip = INPUT_INFO[2]
else:
    raise ValueError('Parameter error, you must use command mode to start the program')
OTHER_IP = [i for i in other_ip.split(',')]

DIRECTORY = 'transmission'
if not os.path.isdir(DIRECTORY):
    os.mkdir(DIRECTORY)

BUFFER_SIZE = 1024
SYSTEM_SEPARATOR = '/'
SOCKET_SEPARATOR = 'sep'
SOCKET_TIMEOUT = 10
MAXIMUM_TRANSFER_SIZE = 1073741824
SERVER_PORT = 6767
CLIENT_PORT = 6767


def recv_data(handle, expected, need_decode=True):
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


def get_md5(file_name):
    with open(file_name, 'rb') as file:
        file_data = file.read()
    diff_check = hashlib.md5()
    diff_check.update(file_data)
    md5_code = diff_check.hexdigest()
    return md5_code


def get_local_file():
    all_files = []
    for root, dirs, files in os.walk(DIRECTORY):
        for each_file in files:
            all_files.append(os.path.join(root, each_file))
    if all_files:
        file_list = []
        for each_file in all_files:
            file_list.append({
                'file': DIRECTORY + each_file.split(DIRECTORY, 1)[-1],
                'md5': get_md5(file_name=each_file),
                'size': os.path.getsize(each_file)
            })
        return file_list
    else:
        return []


def check_directory(files):
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


def config_server(ip, port):
    server = socket.socket()
    server.bind((ip, port))
    server.listen()
    print(f'Start server {ip}:{port}')
    return server


def config_server_side(ip):
    def _config_server_side():
        while True:
            conn, address = server.accept()
            conn.settimeout(SOCKET_TIMEOUT)
            print('connected client：{}'.format(address))
            recv_data(handle=conn, expected='client ok')
            conn.send('server ok'.encode())
            recv_data(handle=conn, expected='request files')
            all_file = get_local_file()
            if all_file:
                conn.send(str(all_file).encode())
            else:
                conn.send('server no data'.encode())
            expect_info = ['no update', 'start update']
            socket_data = recv_data(handle=conn, expected=expect_info)
            if expect_info[0] in socket_data:
                print('no update')
                continue
            conn.send('server received request'.encode())
            while True:
                expect_info = ['all update done', 'detail info']
                socket_data = recv_data(handle=conn, expected=expect_info)
                if expect_info[0] in socket_data:
                    break
                file_name, file_size, file_md5 = socket_data.split(expect_info[1])[-1].split(SOCKET_SEPARATOR)
                conn.send('server received detail info'.encode())
                check_directory(files=file_name)
                data_content = ''.encode()
                while True:
                    socket_data = recv_data(handle=conn, expected='', need_decode=False)
                    if 'file transfer done'.encode() in socket_data:
                        break
                    data_content += socket_data
                    conn.send('received success'.encode())
                with open(file_name, 'wb') as wf:
                    wf.write(data_content)
                new_file_size = str(os.path.getsize(file_name))
                new_file_md5 = get_md5(file_name=file_name)
                if new_file_size != file_size or new_file_md5 != file_md5:
                    conn.send('write error'.encode())
                else:
                    conn.send('write success'.encode())
            time.sleep(5)

    server = config_server(ip, SERVER_PORT)
    while True:
        try:
            _config_server_side()
        except Exception as ex:
            print('Server encounters an error: {}'.format(ex))
            time.sleep(2)


def config_client(ip, port):
    client = socket.socket()
    client.connect((ip, port))
    print(f'connect {ip}:{port} successful')
    return client


def config_client_side(all_remote_ip):
    def _config_client_side():
        while True:
            time.sleep(3)
            for remote_ip in all_remote_ip:
                ip, port = remote_ip, CLIENT_PORT
                client = config_client(ip, port)
                client.settimeout(SOCKET_TIMEOUT)

                client.send('client ok'.encode())
                recv_data(handle=client, expected='server ok')
                client.send('request files'.encode())
                socket_data = recv_data(handle=client, expected='')

                all_file = get_local_file()
                if all_file:
                    if 'server no data' in socket_data:
                        need_sync_files = all_file
                    else:
                        server_file_mapping = {}
                        for server_file in eval(socket_data):
                            server_file_mapping[server_file['file']] = server_file
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
                        client.send('start update'.encode())
                        recv_data(handle=client, expected='server received request')
                        for each_file in need_sync_files:
                            file_name, file_size, file_md5 = each_file['file'], each_file['size'], each_file['md5']
                            if file_size > MAXIMUM_TRANSFER_SIZE:
                                continue
                            while True:
                                file_info = f'{file_name}{SOCKET_SEPARATOR}{file_size}{SOCKET_SEPARATOR}{file_md5}'
                                client.send(f'detail info{file_info}'.encode())
                                recv_data(handle=client, expected='server received detail info')
                                with tqdm.tqdm(desc=f'Send:{file_name}', total=file_size, unit='B',
                                               unit_divisor=1024) as bar:
                                    with open(file_name, 'rb') as rf:
                                        while True:
                                            bytes_read = rf.read(BUFFER_SIZE)
                                            if not bytes_read:
                                                break
                                            client.send(bytes_read)
                                            recv_data(handle=client, expected='received success')
                                            bar.update(len(bytes_read))

                                client.send('file transfer done'.encode())
                                socket_data = recv_data(handle=client, expected='')
                                if 'write error' not in socket_data:
                                    break
                        client.send('all update done'.encode())
                    else:
                        client.send('no update'.encode())
                else:
                    client.send('no update'.encode())
                client.close()
                time.sleep(5)
    while True:
        try:
            _config_client_side()
        except Exception as ex:
            print('Client encounters an error: {}'.format(ex))


if __name__ == '__main__':
    info = os.popen('ifconfig').read()
    result = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', info)
    if result:
        local_ip = result.group(1)
    else:
        raise ValueError('Capture local ip error')
    threading.Thread(target=config_server_side, args=(local_ip,)).start()
    threading.Thread(target=config_client_side, args=(OTHER_IP,)).start()
