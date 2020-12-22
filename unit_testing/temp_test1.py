# -*- coding:utf-8 -*-
import chardet

result = chardet.detect(open(r'C:\Users\evaliu\OneDrive - Cisco\Desktop\\倒计时.exe', mode='rb').read())
print(result)
