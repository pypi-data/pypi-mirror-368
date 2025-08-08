
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.common.Qr import Qr
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
    
                
class QrTestCase(unittest.TestCase):

    def testDescribeTimeStamp(self):
        a = Auth(username, pwd)
        body = {
            'timestamp': 1546847673,
        }
        qr = Qr(a)
        r = qr.describeTimeStamp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Qr', 'describeTimeStamp', body)

    def testObtainQrContent(self):
        a = Auth(username, pwd)
        body = {
            'app_name': 'enterpriseApp',
        }
        qr = Qr(a)
        r = qr.obtainQrContent(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Qr', 'obtainQrContent', body)

    def testCreateQrPic(self):
        a = Auth(username, pwd)
        body = {
            'point_size': 1,
            'text': 'test',
            'format': 'base64',
        }
        qr = Qr(a)
        r = qr.createQrPic(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Qr', 'createQrPic', body)

    def testConfirmLogin(self):
        a = Auth(username, pwd)
        body = {
            'action': 1,
            'uuid': '9169240e9e5fa86a115578b9ed151c34771ca22e',
        }
        qr = Qr(a)
        r = qr.confirmLogin(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Qr', 'confirmLogin', body)

    def testCancelLogin(self):
        a = Auth(username, pwd)
        body = {
            'action': 2,
            'uuid': '9169240e9e5fa86a115578b9ed151c34771ca22e',
        }
        qr = Qr(a)
        r = qr.confirmLogin(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Qr', 'cancelLogin', body)

    def testCheckQrValidity(self):
        a = Auth(username, pwd)
        body = {
            'action': 3,
            'uuid': '9169240e9e5fa86a115578b9ed151c34771ca22e',
        }
        qr = Qr(a)
        r = qr.confirmLogin(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Qr', 'checkQrValidity', body)

    def testCheckQrStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '0d6e290f9c8414bac0bb105b97232771ec3e5178',
        }
        qr = Qr(a)
        r = qr.checkQrStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Qr', 'checkQrStatus', body)


if __name__ == '__main__':
    unittest.main()  
