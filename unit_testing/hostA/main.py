import time
import os
import socket
import re
import threading
import sys

INPUT_INFO = sys.argv
if len(INPUT_INFO) == 3:
    if INPUT_INFO[1] != '--ip':
        raise ValueError('The second parameter should be --ip')
    other_ip = INPUT_INFO[2]
else:
    raise ValueError('Parameter error, you must use command mode to start the program')
OTHER_IP = [i for i in other_ip.split(',')]

r = os.popen('ifconfig')
result = re.search(r'mtu.+?\n.+?inet (\d+\.\d+\.\d+\.\d+).+?netmask', r.read())
if result:
    LOCAL_IP = result.group(1)
else:
    raise ValueError('local host ip not found')

class SocketHandle(object):

    def __init__(self, local_ip, other_ip, file_directory='socket_sync'):
        self.other_ip = [(i, 6699) for i in other_ip]
        self.server_ip = (local_ip, 6699)
        self.directory = file_directory
        self.file_location = os.path.join(os.getcwd(), file_directory)
        self.create_file_store()
        self.buffer_size = 2048

    def create_file_store(self):
        if not os.path.isdir(self.file_location):
            os.mkdir(self.file_location)

    def receive_server_data(self, sender, expected, need_decode=True):
        while True:
            if need_decode:
                server_data = sender.recv(self.buffer_size).decode()
            else:
                server_data = sender.recv(self.buffer_size)
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

    def read_all_file(self):
        total_files = []
        for root, dirs, files in os.walk(self.directory):
            for i in files:
                total_files.append(os.path.join(root, i))
        result = {}
        for index, file in enumerate(total_files, 1):
            result[str(index)] = {
                'filesize': os.path.getsize(file),
                'filepath': self.directory + file.split(self.directory, 1)[-1],
            }
        return result

    @staticmethod
    def inspect_files(file):
        number = -1
        directory = []
        for i in range(len(file.split('/')[:-1]) - 1):
            directory.append('/'.join(file.split('/')[:number]))
            number = number - 1
        for r in sorted(directory, reverse=True):
            if not os.path.isdir(r):
                os.mkdir(r)

    def build_server_services(self):
        server = socket.socket()
        server.bind(self.server_ip)
        server.listen()
        while True:
            try:
                conn, addr = server.accept()
                conn.settimeout(10)
                print('Client {} accessed'.format(addr))
                self.receive_server_data(sender=conn, expected='client setup ok')
                conn.send('server setup ok'.encode())
                self.receive_server_data(sender=conn, expected='request server data')
                total_file = self.read_all_file()
                if total_file:
                    conn.send(str(total_file).encode())
                else:
                    conn.send('no any data'.encode())
                client_data = self.receive_server_data(sender=conn, expected=None)
                if "Don't update" in client_data:
                    continue
                conn.send('received request'.encode())
                while True:
                    client_data = self.receive_server_data(sender=conn, expected=None)
                    if 'all transfer done' in client_data:
                        break
                    filepath, filesize = client_data.split(',')
                    print('received filepath {}, filesize: {}'.format(filepath, filesize))
                    conn.send('received file detail info'.encode())
                    self.inspect_files(file=filepath)
                    data = ''.encode()
                    while True:
                        result = conn.recv(self.buffer_size)
                        if 'file transfer done'.encode() in result:
                            break
                        data += result
                        conn.send('file write ok'.encode())
                    file_write = open(filepath, 'wb')
                    file_write.write(data)
                    file_write.close()
                    print('write {} successful'.format(filepath))
                time.sleep(3)
            except Exception as ex:
                print('Server encounters an error: {}'.format(ex))
                time.sleep(3)

    def build_client_services(self):
        while True:
            client = None
            time.sleep(3)
            try:
                for ips in self.other_ip:
                    client = socket.socket()
                    client.connect(ips)
                    client.settimeout(10)

                    client.send('client setup ok'.encode())
                    self.receive_server_data(sender=client, expected='server setup ok')
                    client.send('request server data'.encode())
                    server_data = self.receive_server_data(sender=client, expected=None)
                    total_file = self.read_all_file()
                    if total_file:
                        if 'no any data' in server_data:
                            transfer_files = total_file
                        else:
                            server_files = {}
                            for key, value in eval(server_data).items():
                                server_files[value['filepath']] = value
                            transfer_files = []
                            for each_file in total_file.values():
                                if each_file['filepath'] not in server_files.keys():
                                    transfer_files.append(each_file)
                                    continue
                        if transfer_files:
                            client.send('start transfer files'.encode())
                            self.receive_server_data(sender=client, expected='received request')
                            for tf in transfer_files:
                                filepath = tf['filepath']
                                filesize = tf['filesize']
                                if filesize > 1073741824:
                                    continue
                                while True:
                                    file_info = '{},{}'.format(filepath, filesize)
                                    client.send(file_info.encode())
                                    self.receive_server_data(sender=client, expected='received file detail info')
                                    with open(filepath, 'rb') as rf:
                                        while True:
                                            bytes_read = rf.read(self.buffer_size)
                                            if not bytes_read:
                                                break
                                            client.send(bytes_read)
                                            result = self.receive_server_data(sender=client, expected='write ok')
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

    def main(self):
        threading.Thread(target=self.build_server_services).start()
        threading.Thread(target=self.build_client_services).start()


if __name__ == '__main__':
    handle = SocketHandle(LOCAL_IP,OTHER_IP)
    handle.main()
