# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.upmonitor.v20220622.UpMonitor import UpMonitor
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


class UpMonitorTestCase(unittest.TestCase):

    def testAuthUpMonitor(self):
        a = Auth(username, pwd)
        body = {
            'access_key': '3f0bfb5a3ab84b2c589869ef95295bb21e6042c0',
            'secret_key': '3f0bfb5a3ab84b2c589869ef95295bb21e6042c0',
            'ip': '127.0.0.1',
            'port': '58086',
        }
        upMonitor = UpMonitor(a)
        r = upMonitor.authUpMonitor(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'UpMonitor', 'authUpMonitor', body)

    def testDescribeUpMonitorToken(self):
        a = Auth(username, pwd)
        body = {
            'up_uuid': '',
        }
        upMonitor = UpMonitor(a)
        r = upMonitor.describeUpMonitorToken(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'UpMonitor', 'describeUpMonitorToken', body)

    def testCreateUpMonitor(self):
        a = Auth(username, pwd)
        body = {
            'access_key': '3f0bfb5a3ab84b2c589869ef95295bb21e6042c0',
            'biz_grp_list': [],
            'comment': '备注xxx',
            'secret_key': '3f0bfb5a3ab84b2c589869ef95295bb21e6042c0',
            'ip': '127.0.0.1',
            'port': '58086',
            'up_uuid': 'CE753C48-96F9-6C38-C3DE-A25E7405D03F',
            'up_name': '就这个控制机',
        }
        upMonitor = UpMonitor(a)
        r = upMonitor.createUpMonitor(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'UpMonitor', 'createUpMonitor', body)

    def testModifyUpMonitor(self):
        a = Auth(username, pwd)
        body = {
            'up_name': '就这个控制机',
            'access_key': 'oishvmn5YPHJcEDaIjtwd0R9Ug7BN1fk',
            'secret_key': 'fkLiyqsG3P1AzB5jWtYbZa7TU8RN9wSVhe6EldOo',
            'ip': '172.20.2.70',
            'port': '58086',
            'comment': '备注xxx',
            'biz_grp_list': [],
            'random_str': '11111111-1111-1111-1111-111111111111',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        upMonitor = UpMonitor(a)
        r = upMonitor.modifyUpMonitor(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'UpMonitor', 'modifyUpMonitor', body)

    def testDescribeUpMonitor(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        upMonitor = UpMonitor(a)
        r = upMonitor.describeUpMonitor(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'UpMonitor', 'describeUpMonitor', body)

    def testListUpMonitor(self):
        a = Auth(username, pwd)
        body = {
            'limit': 1,
            'page': 1,
        }
        upMonitor = UpMonitor(a)
        r = upMonitor.listUpMonitor(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'UpMonitor', 'listUpMonitor', body)

    def testRefreshUpMonitor(self):
        a = Auth(username, pwd)
        body = {
            'up_uuids': [],
            'operate': '',
        }
        upMonitor = UpMonitor(a)
        r = upMonitor.refreshUpMonitor(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'UpMonitor', 'refreshUpMonitor', body)

    def testListUpMonitorStatus(self):
        a = Auth(username, pwd)
        body = {
            'up_uuids': [],
        }
        upMonitor = UpMonitor(a)
        r = upMonitor.listUpMonitorStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'UpMonitor', 'listUpMonitorStatus', body)

    def testDeleteUpMonitor(self):
        a = Auth(username, pwd)
        body = {
            'up_uuids': [],
        }
        upMonitor = UpMonitor(a)
        r = upMonitor.deleteUpMonitor(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'UpMonitor', 'deleteUpMonitor', body)


if __name__ == '__main__':
    unittest.main()
