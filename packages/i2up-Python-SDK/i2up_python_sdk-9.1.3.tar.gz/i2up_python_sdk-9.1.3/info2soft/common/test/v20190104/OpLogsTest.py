
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.common.OpLogs import OpLogs
# from info2soft.common.v20200722.OpLogs import OpLogs
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


class OpLogsTestCase(unittest.TestCase):

    def testListOpLog(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'end': 1548950400,
            'limit': 10,
            'start': 1546272000,
            'op_type': 'delete_nodes',
            'level': 0,
            'description': 'delete_nodes',
            'suffix': '.txt',
            'address': '',
            'username': ''
        }

        opLogs = OpLogs(a)
        r = opLogs.listOpLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OpLogs', 'listOpLog', body)

    def testImportOpLog(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'end': 1548950400,
            'limit': 10,
            'start': 1546272000,
            'op_type': 'delete_nodes',
            'level': 0,
            'description': 'delete_nodes',
            'suffix': '.txt',
            'address': '',
            'username': ''
        }

        opLogs = OpLogs(a)
        r = opLogs.importOpLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OpLogs', 'importOpLog', body)

    def testDownloadOpLog(self):
        a = Auth(username, pwd)
        body = {
            'end_time': 1,
            'start_time': 1,
        }

        opLogs = OpLogs(a)
        r = opLogs.downloadOpLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OpLogs', 'downloadOpLog', body)

    def testDeleteOpLog(self):
        a = Auth(username, pwd)
        body = {
            'end_time': 1,
            'start_time': 1,
        }

        opLogs = OpLogs(a)
        r = opLogs.deleteOpLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OpLogs', 'downloadOpLog', body)

    def testListUserLog(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'start': 1546272000,
            'end': 1548950400,
            'op_type': 'delete_nodes',
            'level': 0,
            'description': 'delete_nodes',
            'suffix': '.txt',
        }

        opLogs = OpLogs(a)
        r = opLogs.listUserLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'OpLogs', 'listUserLog', body)


if __name__ == '__main__':
    unittest.main()
