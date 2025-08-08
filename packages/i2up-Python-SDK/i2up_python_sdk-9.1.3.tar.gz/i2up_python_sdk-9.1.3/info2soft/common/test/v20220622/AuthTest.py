
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.common.Auth import Auth
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
    
                
class AuthTestCase(unittest.TestCase):

    def testDescribeTimeStamp(self):
        a = Auth(username, pwd)
        body = {
            'timestamp': 1546847673,
        }

        r = a.describeTimeStamp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Auth', 'describeTimeStamp', body)

    def testAuthGenerate(self):
        a = Auth(username, pwd)
        body = {
        }

        r = a.authGenerate(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Auth', 'authGenerate', body)

    def testDescribeVerificationCode(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'mobile': 18501767968,
            'email': '',
            'type': 'sms',
        }

        r = a.describeVerificationCode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Auth', 'describeVerificationCode', body)

    def testCheckCaptcha(self):
        a = Auth(username, pwd)
        body = {
            'username': 'admin',
        }

        r = a.checkCaptcha(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Auth', 'checkCaptcha', body)

    def testTokendef(self):
        a = Auth(username, pwd)
        body = {
            'pwd': 'Info1234',
            'username': 'admin',
        }

        r = a.tokendef(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Auth', 'tokendef', body)

    def testHeartbeat(self):
        a = Auth(username, pwd)
        body = {
            'refresh_token': 'null',
        }

        r = a.heartbeat(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Auth', 'heartbeat', body)

    def testResetPwd(self):
        a = Auth(username, pwd)
        body = {
        }

        r = a.resetPwd(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Auth', 'resetPwd', None)

    def testCheckLoginStatus(self):
        a = Auth(username, pwd)
        body = {
            'access_token': 'a10b45cd8b94ad53UEsc8H-gxjMU-jX76eFd2z4eoDh0vlVkPPDWaJyBWssjwWdYAtk4SdFaL8dQH48QQv29c3TRNX3FQo4Ub_V1qwehbRQ28KBEtYqTG6wy8sbAEWPVcBoE2uWXnmP_J5R9hXl8yHbeyaMwMjLpWe0onA',
        }
        r = a.checkLoginStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Auth', 'checkLoginStatus', body)


if __name__ == '__main__':
    unittest.main()  
