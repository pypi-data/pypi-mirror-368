
# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.common.DbConvert import DbConvert
# from info2soft.common.v20200722.DbConvert import DbConvert
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


class DbConvertTestCase(unittest.TestCase):

    def testDbConvertImport(self):
        a = Auth(username, pwd)
        body = {
        }
        
        dbConvert = DbConvert(a)
        r = dbConvert.dbConvertImport(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DbConvert', 'dbConvertImport', body)

    def testDbConvertListConverts(self):
        a = Auth(username, pwd)
        body = {
            'type': '',
        }
        
        dbConvert = DbConvert(a)
        r = dbConvert.dbConvertListConverts(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DbConvert', 'dbConvertListConverts', body)

    def testDbConvertMigrate(self):
        a = Auth(username, pwd)
        body = {
            'version': '',
            'type': '',
        }
        
        dbConvert = DbConvert(a)
        r = dbConvert.dbConvertMigrate(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DbConvert', 'dbConvertMigrate', body)


if __name__ == '__main__':
    unittest.main()
