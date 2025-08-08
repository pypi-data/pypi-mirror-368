
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.resource.v20200930 import Monitor
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
    
                
class MonitorTestCase(unittest.TestCase):

    def testListDriversInfo(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84'
        }
        monitor = Monitor(a)
        r = monitor.listDriversInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Monitor', 'listDriversInfo', body)

    def testListPhyInfo(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84'
        }
        monitor = Monitor(a)
        r = monitor.listPhyInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Monitor', 'listPhyInfo', body)

    def testListChartConfig(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84'
        }
        monitor = Monitor(a)
        r = monitor.listChartConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Monitor', 'listChartConfig', body)

    def testSetChartConfig(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
            'storage_io': 1,
            'nic_io': 0,
            'per_core': 1,
            'per_disk': 0,
            'net_in': 0,
            'net_out': 0,
        }
        monitor = Monitor(a)
        r = monitor.setChartConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Monitor', 'setChartConfig', body)

    def testListChartData(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
            'start_time': 154172680,
            'last_time': 164172680,
        }
        monitor = Monitor(a)
        r = monitor.listChartData(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Monitor', 'listChartData', body)

    def testListBkNodeOverall(self):
        a = Auth(username, pwd)
        body = {
        }

        monitor = Monitor(a)
        r = monitor.listBkNodeOverall(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Monitor', 'listBkNodeOverall', body)


if __name__ == '__main__':
    unittest.main()  
