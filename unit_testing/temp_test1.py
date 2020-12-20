# -*- coding:utf-8 -*-
import re
a = """root@kali:~/桌面/test# ifconfig
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.8.128  netmask 255.255.255.0  broadcast 192.168.8.255
        inet6 fe80::20c:29ff:fe7d:c448  prefixlen 64  scopeid 0x20<link>
        ether 00:0c:29:7d:c4:48  txqueuelen 1000  (Ethernet)
        RX packets 40308  bytes 44925501 (42.8 MiB)
        RX errors 72  dropped 73  overruns 0  frame 0
        TX packets 32057  bytes 6260737 (5.9 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        device interrupt 19  base 0x2000  

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 227768  bytes 79280128 (75.6 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 227768  bytes 79280128 (75.6 MiB)
"""

result = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', a)
if result:
    print(result.group(1))
