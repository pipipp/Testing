"""
Client
"""
import socket
import tqdm
import os
import sys
import hashlib


def get_file_md5(fname):
    m = hashlib.md5()  # ����md5����
    with open(fname, 'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)  # ����md5����

    return m.hexdigest()  # ����md5����


# �����ļ���,�����ļ����б�Ͷ�Ӧmd5
def walkFile(file):
    filelist = []
    md5list = []
    for root, dirs, files in os.walk(file):

        # root ��ʾ��ǰ���ڷ��ʵ��ļ���·��
        # dirs ��ʾ���ļ����µ���Ŀ¼��list
        # files ��ʾ���ļ����µ��ļ�list

        # �����ļ�
        for filename in files:
            filelist.append(os.path.join(root, filename))
            md5list.append(get_file_md5(os.path.join(root, filename)))

    return dict(zip(filelist, md5list))


cfiles = walkFile(os.getcwd())

# �������ݵķָ���
SEPARATOR = "<SEP>"

# ��������Ϣ
host = "192.168.8.128"
port = 20001

# �ļ�����Ļ�����
BUFFER_SIZE = 4096

# �����ļ�������
# filename = "/root/����/python/ppt.rar"

# �ļ���С
# filesize = os.path.getsize(filename)

# ����socket����

while True:
    s = socket.socket()

    # ���ӷ�����
    print(f"������������{host}:{port}")
    s.connect((host, port))
    print("���������ӳɹ���")
    for key in cfiles:
        filename = key
        filesize = os.path.getsize(filename)
        filemd5 = cfiles[key]

        # �����ļ����ֺ��ļ���С��������б��봦��
        s.send(f"{filename}{SEPARATOR}{filesize}{SEPARATOR}{filemd5}".encode())

        # �ļ�����
        progress = tqdm.tqdm(range(filesize), f"����{filename}", unit="B", unit_divisor=1024)
        with open(filename, "rb") as f:
            for _ in progress:
                # ��ȡ�ļ�
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                # sendallȷ������æµʱ��Ȼ���Դ���
                s.sendall(bytes_read)
                progress.update(len(bytes_read))

    s.close()