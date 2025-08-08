
# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.common.FindPassword import FindPassword
# from info2soft.common.v20200722.FindPassword import FindPassword
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


class FindPasswordTestCase(unittest.TestCase):

    def testIsAccountExists(self):
        a = Auth(username, pwd)
        body = {
            'account': '',
            'type': 'email ',
        }
        
        findPassword = FindPassword(a)
        r = findPassword.isAccountExists(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FindPassword', 'isAccountExists', body)

    def testSendVerificationCode(self):
        a = Auth(username, pwd)
        body = {
            'account': '',
            'type': 'mobile',
        }
        
        findPassword = FindPassword(a)
        r = findPassword.sendVerificationCode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FindPassword', 'sendVerificationCode', body)

    def testVerifyVerficationCode(self):
        a = Auth(username, pwd)
        body = {
            'account': '',
            'verification_code': '',
            'type': 'mobile',
        }
        
        findPassword = FindPassword(a)
        r = findPassword.verifyVerficationCode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FindPassword', 'verifyVerficationCode', body)

    def testResetPassword(self):
        a = Auth(username, pwd)
        body = {
            'account': '',
            'password': '',
            'type': '',
            'verification_code': '',
        }
        
        findPassword = FindPassword(a)
        r = findPassword.resetPassword(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FindPassword', 'resetPassword', body)


if __name__ == '__main__':
    unittest.main()
