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

        # root ��ʾ��ǰ���ڷ��ʵ��ļ���·��
        # dirs ��ʾ���ļ����µ���Ŀ¼��list
        # files ��ʾ���ļ����µ��ļ�list

        # �����ļ�
        for filename in files:
            filelist.append(os.path.join(root, filename))

    return filelist


server = socket.socket()
server.bind(('192.168.8.128', 30000))
server.listen()
print('�ȴ��ͻ�������')

while True:
    conn, addr = server.accept()
    print('��ǰ���ӿͻ��ˣ�', addr)

    while True:
        files = walkFile(os.getcwd())
        filelist = ','.join(files)
        conn.send(filelist.encode())
        print('�ȴ��ͻ�������ָ��')

        data = conn.recv(1024)
        if not data:
            print('�ͻ����ѶϿ�����')
            break
        filename = data.decode()
        if os.path.isfile(filename):  # �ж��ļ��Ƿ����
            f = open(filename, 'rb')
            m = hashlib.md5()
            file_size = os.stat(filename).st_size  # ��ȡ�ļ���С
            conn.send(str(file_size).encode())  # �����ļ���С
            conn.recv(1024)  # �ȴ�ȷ��
            for line in f:
                conn.send(line)  # �����ļ�
                m.update(line)
            print("�ļ�md5ֵ��", m.hexdigest())
            conn.send(m.hexdigest().encode())  # ����md5ֵ
            f.close()
        print('�������')
server.close()
