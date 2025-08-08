
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.tools.v20181227.Compare import Compare
from info2soft import Auth
from info2soft.fileWriter import write
from info2soft.compat import is_py2, is_py3

if is_py2:
    import sys
    import StringIO
    import urllib

    # reload(sys)
    sys.setdefaultencoding('utf-8')
    StringIO = StringIO.StringIO
    urlopen = urllib.urlopen
if is_py3:
    import io
    import urllib

    StringIO = io.StringIO
    urlopen = urllib.request.urlopen

username = 'admin'
pwd = 'Info1234'
    
                
class CompareTestCase(unittest.TestCase):

    def testCreateCompare(self):
        a = Auth(username, pwd)
        body = {
            'compare': {
                'excl_path': [],
                'bkup_one_time': 0,
                'bkup_schedule': {
                    'sched_gap_min': 60,
                    'sched_time': ['00:00:00', ],
                    'sched_day': ['1', ],
                    'sched_time_end': '23:59',
                    'limit': 5,
                    'sched_time_start': '00:00',
                    'sched_every': 0,
                },
                'mirr_file_check': '1',
                'task_name': 'testCompare1',
                'wk_path': ['E:\\test\\', ],
                'bk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                'cmp_type': 0,
                'bk_path': ['E:\\test\\', ],
                'bkup_policy': 2,
                'compress': 0,
                'wk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            },
        }
        compare = Compare(a)
        r = compare.createCompare(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Compare', 'createCompare', body)

    def testModifyCompare(self):
        a = Auth(username, pwd)
        body = {
            'compare': {
            'excl_path': [],
            'bkup_one_time': 0,
            'bkup_schedule': {
            'sched_gap_min': 60,
            'sched_time': [
            '00:00:00',],
            'sched_day': [
            '1',],
            'sched_time_end': '23:59',
            'limit': 5,
            'sched_time_start': '00:00',
            'sched_every': 0,},
            'mirr_file_check': '1',
            'task_name': 'testCompare1',
            'wk_path': [
            'E:\\test\\',],
            'bk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'cmp_type': 0,
            'bk_path': [
            'E:\\test\\',],
            'bkup_policy': 2,
            'compress': 0,
            'wk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'mirr_sync_attr': 1,
            'encrypt_switch': '',
            'secret_key': '',
            'biz_grp_list': [],
            'oph_policy': '',
            'ct_name_str1': '',
            'ct_name_str2': '',
            'ct_name_str3': '',
            'ct_name_str4': '',
            'task_uuid': '',
            'random_str': '',
            'data_ip_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',},
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        compare = Compare(a)
        r = compare.modifyCompare(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Compare', 'modifyCompare', body)

    def testListCompareLogs(self):
        a = Auth(username, pwd)
        body = {
        }

        compare = Compare(a)
        r = compare.listCompareLogs(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Compare', 'listCompareLogs', body)

    def testDescribeCompare(self):
        a = Auth(username, pwd)
        body = {
            'compare': {
                'task_uuid': '88FE607E-6826-5F1F-FC70-9B3036DA79C6'
            }
        }
        compare = Compare(a)
        r = compare.describeCompare(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Compare', 'describeCompare', body)

    def testDescribeCompareResults(self):
        a = Auth(username, pwd)
        compare = Compare(a)
        r = compare.describeCompareResults()
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Compare', 'describeCompareResults', {})

    def testListCompare(self):
        a = Auth(username, pwd)
        body = {
            'search_value': '',
            'limit': 10,
            'page': 1,
            'search_field': '',
        }
        compare = Compare(a)
        r = compare.listCompare(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Compare', 'listCompare', body)

    def testListCircleCompareResult(self):
        a = Auth(username, pwd)
        body = {
            'task_uuid': '88FE607E-6826-5F1F-FC70-9B3036DA79C6',
            'search_field': '',
            'limit': 10,
            'search_value': '',
            'page': 1,
        }
        compare = Compare(a)
        r = compare.listCircleCompareResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Compare', 'listCircleCompareResult', body)

    def testListCompareStatus(self):
        a = Auth(username, pwd)
        body = {
            'task_uuids': ['88FE607E-6826-5F1F-FC70-9B3036DA79C6'],
        }
        compare = Compare(a)
        r = compare.listCompareStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Compare', 'listCompareStatus', body)

    def testDownloadCompare(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'download',
            'task_uuids': ['88FE607E-6826-5F1F-FC70-9B3036DA79C6'],
        }
        compare = Compare(a)
        r = compare.downloadCompare(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Compare', 'downloadCompare', body)

    def testStartImmediatelyCompare(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start_immediate',
            'task_uuids': ['88FE607E-6826-5F1F-FC70-9B3036DA79C6'],
        }
        compare = Compare(a)
        r = compare.startImmediatelyCompare(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Compare', 'startImmediatelyCompare', body)

    def testDeleteCompare(self):
        a = Auth(username, pwd)
        body = {
            'task_uuids': ['88FE607E-6826-5F1F-FC70-9B3036DA79C6'],
        }
        compare = Compare(a)
        r = compare.deleteCompare(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Compare', 'deleteCompare', body)

    def testCollectCompareResult(self):
        a = Auth(username, pwd)
        body = {
            'code': '',
            'time': '',
            'files': '',
            'bytes': '',
            'missing': '',
            'diff': '',
            'erro': '',
            'equal': '',
            'task_uuid': '',
        }

        compare = Compare(a)
        r = compare.collectCompareResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Compare', 'collectCompareResult', body)


if __name__ == '__main__':
    unittest.main()  
