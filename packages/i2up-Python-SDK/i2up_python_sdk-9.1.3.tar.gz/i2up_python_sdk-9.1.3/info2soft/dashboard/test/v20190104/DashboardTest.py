
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.dashboard.v20181227.Dashboard import Dashboard
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
    
                
class DashboardTestCase(unittest.TestCase):

    def testDescribeVpRuleRate(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'wk_uuid': 'F28BA5A6-4FF9-E596-4371-1ED203D45143',
            'mode': 'month',
            'type': 'I2VP_BK',
            'group_uuid': '',
        }
        dashboard = Dashboard(a)
        r = dashboard.describeVpRuleRate(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Dashboard', 'describeVpRuleRate', body)

    def testDescribeVmProtectRate(self):
        a = Auth(username, pwd)
        body = {
            'vp_uuid': 'F28BA5A6-4FF9-E596-4371-1ED203D45143',
        }
        dashboard = Dashboard(a)
        r = dashboard.describeVmProtectRate(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Dashboard', 'describeVmProtectRate', body)

    def testRepBackup(self):
        a = Auth(username, pwd)
        dashboard = Dashboard(a)
        body = {
            'limit': 10,
            'page': 1,
            'type': 0
        }
        r = dashboard.repBackup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Dashboard', 'repBackup', body)

    def testNode(self):
        a = Auth(username, pwd)
        dashboard = Dashboard(a)
        body = {
            'limit': 10,
            'page': 1,
            'type': 0
        }
        r = dashboard.node(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Dashboard', 'node', body)

    def testHa(self):
        a = Auth(username, pwd)
        dashboard = Dashboard(a)
        body = {
            'limit': 10,
            'page': 1,
            'type': 0
        }
        r = dashboard.ha(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Dashboard', 'ha', body)


if __name__ == '__main__':
    unittest.main()  
