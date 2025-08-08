
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
# from info2soft import Authorization
from info2soft.resource.v20200930.Authorization import Authorization
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


class AuthorizationTestCase(unittest.TestCase):

    def testListAuthorizationUser(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 1,
        }

        authorization = Authorization(a)
        r = authorization.ListAuthorizationUser(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Authorization', 'ListAuthorizationUser', body)

    def testGetAuthorizationUserBind(self):
        a = Auth(username, pwd)
        body = {
            'user_uuid': '',
            'page': 1,
            'limit': 1,
            'type': '',
            'subtype': '',
        }
        
        authorization = Authorization(a)
        r = authorization.getAuthorizationUserBind(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Authorization', 'getAuthorizationUserBind', body)

    def testUpdateAuthorizationUserBind(self):
        a = Auth(username, pwd)
        body = {
            'res_list': [{
            'res_uuid': '11111111-1111-1111-1111-111111111111',
            'can_up': 1,
            'can_op': 1,
            'is_bound': 1,},],
            'user_uuid': '11111111-1111-1111-1111-111111111111',
        }
        
        authorization = Authorization(a)
        r = authorization.updateAuthorizationUserBind(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Authorization', 'updateAuthorizationUserBind', body)

    def testGetAuthorizationResBind(self):
        a = Auth(username, pwd)
        body = {
            'res_uuid': '',
            'page': 1,
            'limit': 1,
        }
        
        authorization = Authorization(a)
        r = authorization.getAuthorizationResBind(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Authorization', 'getAuthorizationResBind', body)

    def testUpdateAuthorizationResBind(self):
        a = Auth(username, pwd)
        body = {
            'res_uuid': '',
            'user_list': [{
            'user_uuid': '',
            'can_up': 1,
            'can_op': 1,},],
        }
        
        authorization = Authorization(a)
        r = authorization.updateAuthorizationResBind(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Authorization', 'updateAuthorizationResBind', body)

    def testGetAuthorizationBind(self):
        a = Auth(username, pwd)
        body = {
            'user_uuid': 'EFB53F11-7BA2-2001-3418-85865EA58E47',
        }
        
        authorization = Authorization(a)
        r = authorization.getAuthorizationBind(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Authorization', 'getAuthorizationBind', body)

    def testUpdateAuthorizationBind(self):
        a = Auth(username, pwd)
        body = {
            'user_uuid': 'EFB53F11-7BA2-2001-3418-85865EA58E47',
            'res_uuids': [
            '7E36A0B7-7C9A-D310-645A-F9FF7972F13F',],
        }
        
        authorization = Authorization(a)
        r = authorization.updateAuthorizationBind(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Authorization', 'updateAuthorizationBind', body)


if __name__ == '__main__':
    unittest.main()
