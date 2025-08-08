
# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.resource.v20200930.ReCyle import ReCyle
# from info2soft.resource.v20200722.ReCyle import ReCyle
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


class ReCyleTestCase(unittest.TestCase):

    def testListRecycle(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 1,
            'type': '',
            'where_args[]': '',
        }
        
        reCyle = ReCyle(a)
        r = reCyle.listRecycle(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ReCyle', 'listRecycle', body)

    def testDeleteRecycle(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        reCyle = ReCyle(a)
        r = reCyle.deleteRecycle(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ReCyle', 'deleteRecycle', body)

    def testListRecycleStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        reCyle = ReCyle(a)
        r = reCyle.listRecycleStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ReCyle', 'listRecycleStatus', body)


if __name__ == '__main__':
    unittest.main()
