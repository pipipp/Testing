import argparse
import threading
from server_side import start_server_services
from client_side import start_client_side
from tool import *

parser = argparse.ArgumentParser()
parser.add_argument("-ip", "--ip")
args = parser.parse_args()
assert args.ip, '程序启动失败，参数有误'


def main():
    server_ip = get_local_ip()
    remote_ip = args.ip.split(',')
    print(f'server_ip: {server_ip}')
    print(f'remote_ip: {remote_ip}')

    create_directory(DIRECTORY)
    threading.Thread(target=start_server_services, args=(server_ip, )).start()
    threading.Thread(target=start_client_side, args=(remote_ip, )).start()


if __name__ == '__main__':
    main()
