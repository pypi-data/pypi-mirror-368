
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.common.GeneralInterface import GeneralInterface
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
    
                
class GeneralInterfaceTestCase(unittest.TestCase):

    def testDescribeVersion(self):
        a = Auth(username, pwd)
        body = {
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.describeVersion(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'describeVersion', body)

    def testLatestVersion(self):
        a = Auth(username, pwd)
        body = {
            'plat': 'example_plat',
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.latestVersion(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'latestVersion', body)

    def testListVersionHistory(self):
        a = Auth(username, pwd)
        body = {
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.listVersionHistory(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'listVersionHistory', body)

    def testUpdateDatabase(self):
        a = Auth(username, pwd)
        body = {
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.updateDatabase(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'updateDatabase', body)

    def testNodeConnectTest(self):
        a = Auth(username, pwd)
        body = {
            'ip': '',
            'port': '',
            'type': 'node',
            'node_uuids': [],
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.nodeConnectTest(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'nodeConnectTest', body)

    def testOverall(self):
        a = Auth(username, pwd)
        body = {
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.overall(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'overall', body)

    def testUpMonitorOverall(self):
        a = Auth(username, pwd)
        body = {
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.upMonitorOverall(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'upMonitorOverall', body)

    def testSysadmin(self):
        a = Auth(username, pwd)
        body = {
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.sysadmin(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'sysadmin', body)

    def testStatusOverall(self):
        a = Auth(username, pwd)
        body = {
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.statusOverall(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'statusOverall', body)

    def testListOverallLogs(self):
        a = Auth(username, pwd)
        body = {
            'get_all': 0,
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.listOverallLogs(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'listOverallLogs', body)

    def testListOverallResourceSta(self):
        a = Auth(username, pwd)
        body = {
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.listOverallResourceSta(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'listOverallResourceSta', body)

    def testListOverallRealTimeCopy(self):
        a = Auth(username, pwd)
        body = {
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.listOverallRealTimeCopy(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'listOverallRealTimeCopy', body)

    def testListOverallHa(self):
        a = Auth(username, pwd)
        body = {
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.listOverallHa(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'listOverallHa', body)

    def testListOverallCdm(self):
        a = Auth(username, pwd)
        body = {
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.listOverallCdm(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'listOverallCdm', body)

    def testListOverallFspMv(self):
        a = Auth(username, pwd)
        body = {
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.listOverallFspMv(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'listOverallFspMv', body)

    def testNodeRepSummary(self):
        a = Auth(username, pwd)
        body = {
            'summary': '',
            'cache': '',
            'rep_rule': '',
            'filter': '',
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.nodeRepSummary(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'nodeRepSummary', body)

    def testListVpRuleStat(self):
        a = Auth(username, pwd)
        body = {
            'type': 'VP_PT',
            'wk_uuid': 'AC7A5A1F-5BB1-41D6-E075-1648ADC5C60B',
            'mode': 'month',
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.listVpRuleStat(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'listVpRuleStat', body)

    def testExportRules(self):
        a = Auth(username, pwd)
        body = {
            'suffix': '',
            'type': '',
            'sub_type': '',
            'uuids': [],
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.exportRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'exportRules', body)

    def testCreateColumnExt(self):
        a = Auth(username, pwd)
        body = {
            'type': '',
            'list_col': {
            'wk_ip': {
            'display': '1',
            'width': '100',},
            'bk_ip': {
            'display': '1',},
            'cdp_switch': {
            'display': '1',},
            'name': {
            'display': 1,
            'width': 80,},},
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.createColumnExt(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'createColumnExt', body)

    def testDescribeColumnext(self):
        a = Auth(username, pwd)
        body = {
            'type': '',
        }

        generalInterface = GeneralInterface(a)
        r = generalInterface.describeColumnext(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GeneralInterface', 'describeColumnext', body)


if __name__ == '__main__':
    unittest.main()  
