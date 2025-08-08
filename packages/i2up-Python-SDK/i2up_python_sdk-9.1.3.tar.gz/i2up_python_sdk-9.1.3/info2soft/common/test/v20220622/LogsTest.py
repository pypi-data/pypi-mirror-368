# -*- coding: utf-8 -*-
# flake8: noqa
import sys

sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.common.Logs import Logs
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


class LogsTestCase(unittest.TestCase):

    def testListTaskLog(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'F97B3FD5-4D5D-41EE-22A9-740A74E1E13C',
            'level': 1,
            'start': 1,
            'page': 1,
            'end': 1,
            'limit': 10,
        }

        logs = Logs(a)
        r = logs.listTaskLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Logs', 'listTaskLog', body)

    def testListHALog(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'end': 1,
            'level': 1,
            'start': 1,
            'node_uuid': '',
            'page': 1,
            'limit': 1,
        }

        logs = Logs(a)
        r = logs.listHALog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Logs', 'listHALog', body)

    def testListNodeLog(self):
        a = Auth(username, pwd)
        body = {
            'level': 1,
            'page': 1,
            'limit': 10,
            'start': 1,
            'uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'end': 1,
        }

        logs = Logs(a)
        r = logs.listNodeLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Logs', 'listNodeLog', body)

    def testListNpsvrLog(self):
        a = Auth(username, pwd)
        body = {
        }

        logs = Logs(a)
        r = logs.listNpsvrLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Logs', 'listNpsvrLog', body)

    def testListTrafficLog(self):
        a = Auth(username, pwd)
        body = {
            'start_stamp': 1545637314,
            'type': 'month',
            'uuid': 'F97B3FD5-4D5D-41EE-22A9-740A74E1E13C',
        }

        logs = Logs(a)
        r = logs.listTrafficLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Logs', 'listTrafficLog', body)

    def testCollectStatistics(self):
        a = Auth(username, pwd)
        body = {
            'bkup_window': '00:00-00:00',
            'create_time': '2019-09-02 09:18:44',
            'data_writed_num': '0',
            'dir_failed_num': '--',
            'dup_rate': '0',
            'end_time': '2019-09-02 09:14:00',
            'file_skiped_num': 0,
            'name': 'g',
            'policy': 3,
            'project_failed_num': '',
            'result': 0,
            'space_occu': '0',
            'src_size': '0',
            'src_type': 2,
            'stage': 0,
            'start_time': '2019-09-02 09:14:00',
            'sync_obj_num': 0,
            'tran_rate': '0',
            'trans_data_num': '0',
            'type': 'I2BAK_BK',
            'used_time': '0',
            'uuid': 'C2CE5A8C-79FA-AFA3-1382-1B434B393BC2',
            'wk_uuid': 'C2CE5A8C-79FA-AFA3-1382-1B434B393BC2',
            'bk_uuid': 'C2CE5A8C-79FA-AFA3-1382-1B434B393BC2',
            'other_uuid': 'C2CE5A8C-79FA-AFA3-1382-1B434B393BC2',
            'version_time': '2019-09-02 09:14:00',
            'error_message': '""',
            'data_type': 'o',
        }

        logs = Logs(a)
        r = logs.collectStatistics(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Logs', 'collectStatistics', body)


if __name__ == '__main__':
    unittest.main()  
