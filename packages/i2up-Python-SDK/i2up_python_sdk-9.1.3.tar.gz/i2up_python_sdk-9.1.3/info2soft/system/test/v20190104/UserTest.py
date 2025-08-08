
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.system.v20181227.User import User
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
    
                
class UserTestCase(unittest.TestCase):

    def testCreateUser(self):
        a = Auth(username, pwd)
        body = {
            'username': 'test2',
            'password': '11111111',
            'roles': ['3'],
            'active': '1',
            'email': '11@info2soft.com',
            'mobile': '12366666666',
            'comment': '',
        }
        user = User(a)
        r = user.createUser(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'User', 'createUser', body)

    def testListUser(self):
        a = Auth(username, pwd)
        body = {
            'limit': 10,
            'page': 1,
        }
        user = User(a)
        r = user.listUser(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'User', 'listUser', body)

    def testDescribeUser(self):
        a = Auth(username, pwd)
        body = {
            'user_uuid': '11111111-1111-1111-1111-111111111111'
        }
        user = User(a)
        r = user.describeUser(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'User', 'describeUser', body)

    def testDeleteUser(self):
        a = Auth(username, pwd)
        body = {
            'ids': ['20'],
        }
        user = User(a)
        r = user.deleteUser(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'User', 'deleteUser', body)

    def testModifyUser(self):
        a = Auth(username, pwd)
        body = {
            'ids': '20',
            'username': 'admin',
            'password': 'Info1234',
            'roles': ['3'],
            'active': '1',
            'email': '123@info2soft.com',
            'mobile': '12332145248',
            'comment': '',
            'first_name': '',
            'last_name': '',
        }
        user = User(a)
        r = user.modifyUser(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'User', 'modifyUser', body)

    def testModifyUserPwd(self):
        a = Auth(username, pwd)
        body = {
            'old_password': 'Info1234',
            'password': 'Info1234',
        }
        user = User(a)
        r = user.modifyUserPwd(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'User', 'modifyUserPwd', body)

    def testListProfile(self):
        a = Auth(username, pwd)
        body = {}
        user = User(a)
        r = user.listProfile()
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'User', 'listProfile', body)

    def testModifyProfile(self):
        a = Auth(username, pwd)
        body = {
            'mobile': '15354254585',
            'email': 'test@info2soft.com',
            'nickname': 'test',
            'company': 'info2soft',
            'address': 'test',
            'comment': '',
        }
        user = User(a)
        r = user.modifyProfile(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'User', 'modifyProfile', body)

    def testLogout(self):
        a = Auth(username, pwd)
        body = {}
        user = User(a)
        r = user.logout()
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'User', 'logout', body)


if __name__ == '__main__':
    unittest.main()  
