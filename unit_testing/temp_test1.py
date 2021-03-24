import json
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
restime = []
OK = []


class Restime():
    def API(self, URL2, param):
        try:
            r = requests.get(URL2, params=param, timeout=10)
            r.raise_for_status()  # �����Ӧ״̬�벻�� 200���������׳��쳣
        except requests.RequestException as e:
            print(e)
        else:
            js = json.dumps(r.json())
            return [r.json(), r.elapsed.total_seconds(), js]

    def circulation(self, num, URL2, param):
        for i in range(num):
            restime.append(Restime.API(URL2, param)[1])
            if json.loads(Restime.API(URL2, param)[2])["message"] == 'ok':
                OK.append(json.loads(Restime.API(URL2, param)[2])["message"])
                logger.info('�����' + str(i + 1) + '�Σ�����' + json.loads(Restime.API(URL2, param)[2])["message"] + ',״̬�룺' +
                            json.loads(Restime.API(URL2, param)[2])["status"])
            else:
                logger.info('�����' + str(i + 1) + '�Σ�����' + json.loads(Restime.API(URL2, param)[2])["message"] + ',״̬�룺' +
                            json.loads(Restime.API(URL2, param)[2])["status"])
        print('���Դ�����', num)
        print('��Ӧ������', len(restime))
        print('������Ӧ������', len(OK))
        print('����Ӧ���ʱ����', max(restime))
        print('����Ӧ��Сʱ����', min(restime))
        print('����Ӧʱ����', sum(restime))
        print('ƽ����Ӧʱ����', sum(restime) / len(restime))


if __name__ == '__main__':
    Restime = Restime()
    # URL2 = 'http://wthrcdn.etouch.cn/weather_mini'
    # param = {'ip': '8.8.8.8', 'city': '����'}
    num = 500  # ѹ�����Դ���
    URL2 = 'http://www.kuaidi100.com/query'  # ��ַ
    param = {'type': 'zhongtong', 'postid': '73116039505988'}  # ����
    Restime.circulation(num, URL2, param)
    input('Press Enter to exit...')
