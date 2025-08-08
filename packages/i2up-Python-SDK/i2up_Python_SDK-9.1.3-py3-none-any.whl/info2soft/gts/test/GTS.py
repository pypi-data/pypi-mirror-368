# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.gts.v20181227.GTS import GTS
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


class GTSTestCase(unittest.TestCase):

    def testDescribeLic(self):
        a = Auth(username, pwd)
        body = {
            'num': 1,
            'sn': ['20-4570098558-01'],
            'key': '5BrDir',
            'sign': '',
            'license': {
                '20-4570098558-01': {
                    'feature': 'cdp',
                    'lic': 'joEsLGQImYbDo2/DSG2RGR7VorckQmnPAAvFgLNCVd78KFDFb0Y0xtShHFyQVF6VXRUcHvyeqJEu1'
                           '/nuMOyyJiO8RMoU4GHZMrK6iLDRoPZHV87tp0Jd80MfuTHrpBc209IjM+AkSsTM66Wdfy0tvLJMfPqhaYdg7M80X'
                           '+fhRfeP6kj9ikSVvmJMHJ/ms7lrgz5D+s9jhtzW7tv9cz07bbankTgwyZf6rnjbgOI76tsKzYq8rsBttYSGf'
                           '+oy1qa2nM7x/pQHE6oRiXVy8+Ju2dzpwvLlMurF75r7lWyMRPSniPHBQGrx4yEEeKVwuWCMRaSJVyId13qyP7'
                           'gPBqes4jgsiVHvt1okhydrAeoq89KOgnOHPqrpS+qI9dvXFmFRiP9AB0i9ra67tDx5ItYNh/neNgxsNpV3q0T'
                           'f9PfoTKiKwcYMg0AiFeKuSpynDIL530Ek8Jm/7LbXU7+mUkeGO7BJo9gxEMJRTHuSRLCLIXWm2LY2S58WccsXkL7'
                           'GFaamkh6lE1VX3quXavLpHC0ishL4D0ocEdAh507s6GKd59oVErFAyBOifEE9EONR+95wD9MQMc4SdNt4l4Z7ATj6'
                           '7JN86UFZ5xZpGEOnMgCSUuuzX/Nx0HSF6uUf3Zs6HcViudmXcvLwwaFeRScRDwHYVLhiABda/qAp8Ovoc8Aw/3w='
                }
            },
            'is_trial': 1,
        }
        gts = GTS(a)
        r = gts.describeLic(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GTS', 'describeLic', body)

    def testCloseService(self):
        a = Auth(username, pwd)
        body = {
        }
        gts = GTS(a)
        r = gts.closeService(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GTS', 'closeService', body)

    def testListService(self):
        a = Auth(username, pwd)
        body = {
            'tenant_id@guid': '',
        }
        gts = GTS(a)
        r = gts.listService(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GTS', 'listService', body)

    def testCreateServer(self):
        a = Auth(username, pwd)
        body = {
            'ip': '205.213.117.249',
        }
        gts = GTS(a)
        r = gts.createServer(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GTS', 'createServer', body)

    def testDescribeQuota(self):
        a = Auth(username, pwd)
        body = {
        }
        gts = GTS(a)
        r = gts.describeQuota(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GTS', 'describeQuota', body)

    def testDescribeSummary(self):
        a = Auth(username, pwd)
        body = {
        }
        gts = GTS(a)
        r = gts.describeSummary(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GTS', 'describeSummary', body)

    def testTempFuncName(self):
        a = Auth(username, pwd)
        body = {
        }
        gts = GTS(a)
        r = gts.tempFuncName(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GTS', 'tempFuncName', body)

    def testTempFuncName(self):
        a = Auth(username, pwd)
        body = {
            'tenant_id': '1',
            'mode': 0,
            'service_type': 0,
            'service_period': 30,
            'move_num': 0,
            'phy_num': 1,
            'vm_num': 0,
        }
        gts = GTS(a)
        r = gts.tempFuncName(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GTS', 'tempFuncName', body)

    def testTempFuncName(self):
        a = Auth(username, pwd)
        body = {
            'service_uuid': '1',
            'mode': 0,
            'service_period': 30,
            'move_num': 0,
            'phy_num': 1,
            'vm_num': 0,
        }
        gts = GTS(a)
        r = gts.tempFuncName(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'GTS', 'tempFuncName', body)


if __name__ == '__main__':
    unittest.main()  
