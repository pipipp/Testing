import unittest

from interface_testing.udts_api_test.test_case.case_top import CaseTop
from interface_testing.udts_api_test.public_module.function_module import read_excel


TEST_FILE_NAME = 'test_api.xlsx'


def read_test_file():
    """
    读取测试文件的所有用例
    :return: 返回 active 为 Y 的所有行
    {
        case_number_1: { data1, data2, data3 ... },
        case_number_2: { data1, data2, data3 ... },
        case_number_3: { data1, data2, data3 ... },
    }
    """
    data = read_excel(filename=TEST_FILE_NAME)
    ready_dict = {}
    for row in data:
        temp = dict(
            case_number=row[0],
            api_host=row[2],
            request_url=row[3],
            request_method=row[4],
            request_type=row[5],
            precondition=row[6],
            request_data=row[7],
            check_point=row[8],
            active=row[9],
        )
        if temp['active'].upper() == 'Y':
            ready_dict[temp['case_number']] = temp
    return ready_dict


CASE_RAW_DATA = read_test_file()


class TestAPI(CaseTop):

    @unittest.skipUnless(CASE_RAW_DATA.get('proxy_001'), 'Skip')
    def test_proxy_001(self):
        self.start_case(**CASE_RAW_DATA['proxy_001'])

    @unittest.skipUnless(CASE_RAW_DATA.get('proxy_002'), 'Skip')
    def test_proxy_002(self):
        self.start_case(**CASE_RAW_DATA['proxy_002'])
