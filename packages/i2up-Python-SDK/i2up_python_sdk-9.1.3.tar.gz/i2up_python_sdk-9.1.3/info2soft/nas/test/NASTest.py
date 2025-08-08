
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.nas.v20190102.NAS import NAS
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
    
                
class NASTestCase(unittest.TestCase):

    def testCreateNAS(self):
        a = Auth(username, pwd)
        nas = NAS(a)
        body = {}
        r = nas.createNAS(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Nas', 'createNAS', body)

    def testDescribeNASGroup(self):
        a = Auth(username, pwd)
        nas = NAS(a)
        body = {}
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        r = nas.describeNASGroup(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Nas', 'describeNASGroup', body)

    def testModifyNAS(self):
        a = Auth(username, pwd)
        body = {
            'random_str': '11111111-1111-1111-1111-111111111111',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        nAS = NAS(a)
        r = nAS.modifyNAS(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NAS', 'modifyNAS', body)

    def testListNAS(self):
        a = Auth(username, pwd)
        nas = NAS(a)
        body = {}
        r = nas.listNAS(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Nas', 'listNAS', body)

    def testListNASStatus(self):
        a = Auth(username, pwd)
        nas = NAS(a)
        body = {}
        r = nas.listNASStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Nas', 'listNASStatus', body)

    def testDeleteNAS(self):
        a = Auth(username, pwd)
        nas = NAS(a)
        body = {}
        r = nas.deleteNAS(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Nas', 'deleteNAS', body)

    def testStartNAS(self):
        a = Auth(username, pwd)
        nas = NAS(a)
        body = {}
        r = nas.startNAS(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Nas', 'startNAS', body)

    def testStopNAS(self):
        a = Auth(username, pwd)
        nas = NAS(a)
        body = {}
        r = nas.stopNAS(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Nas', 'stopNAS', body)


if __name__ == '__main__':
    unittest.main()  
