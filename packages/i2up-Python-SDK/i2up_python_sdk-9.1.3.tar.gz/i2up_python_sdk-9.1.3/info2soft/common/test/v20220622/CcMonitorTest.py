
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.common.CcMonitor import CcMonitor
# from info2soft.common.v20200722.CcMonitor import CcMonitor
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


class CcMonitorTestCase(unittest.TestCase):

    def testListCcMonitor(self):
        a = Auth(username, pwd)
        body = {
        }
        
        ccMonitor = CcMonitor(a)
        r = ccMonitor.listCcMonitor(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'CcMonitor', 'listCcMonitor', body)

    def testListNodeStatus(self):
        a = Auth(username, pwd)
        body = {
            'node_ip': '',
            'start_time': 1,
            'last_time': 1,
        }
        
        ccMonitor = CcMonitor(a)
        r = ccMonitor.listNodeStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'CcMonitor', 'listNodeStatus', body)


if __name__ == '__main__':
    unittest.main()
