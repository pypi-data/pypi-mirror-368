
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.system.v20220622.User import User
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

    def testListAk(self):
        a = Auth(username, pwd)
        body = {
        }
        user = User(a)
        r = user.listAk(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'User', 'listAk', body)

    def testCreateAk(self):
        a = Auth(username, pwd)
        body = {
        }
        user = User(a)
        r = user.createAk(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'User', 'createAk', body)

    def testModifyAk(self):
        a = Auth(username, pwd)
        body = {
            'access_key': 'VqUyHS2YQkxnAEZBjFP38e9ht7IaJNlO',
            'status': 0,
        }
        user = User(a)
        r = user.modifyAk(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'User', 'modifyAk', body)

    def testDeleteAk(self):
        a = Auth(username, pwd)
        body = {
            'access_key': 'VqUyHS2YQkxnAEZBjFP38e9ht7IaJNlO',
        }
        user = User(a)
        r = user.deleteAk(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'User', 'deleteAk', body)

    def testListRole(self):
        a = Auth(username, pwd)
        body = {
            'filter_value': 'operator',
            'filter_type': 'name',
            'page': '1',
            'limit': '10',
        }
        user = User(a)
        r = user.listRole(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'User', 'listRole', body)


if __name__ == '__main__':
    unittest.main()  
