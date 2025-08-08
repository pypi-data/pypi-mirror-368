
# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.resource.v20220622.AppType import AppType
# from info2soft.resource.v20200722.AppType import AppType
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


class AppTypeTestCase(unittest.TestCase):

    def testCreateAppType(self):
        a = Auth(username, pwd)
        body = {
            'type_name': 'db',
            'comment': '',
        }
        
        appType = AppType(a)
        r = appType.createAppType(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppType', 'createAppType', body)

    def testListAppType(self):
        a = Auth(username, pwd)
        body = {
        }
        
        appType = AppType(a)
        r = appType.listAppType(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppType', 'listAppType', body)

    def testDescribeAppType(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        appType = AppType(a)
        r = appType.describeAppType(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppType', 'describeAppType', body)

    def testModifyAppType(self):
        a = Auth(username, pwd)
        body = {
            'type_name': 'db1',
            'comment': '',
            'random_str': 'AD23C737-9395-4032-F5C3-F93E84C67D47',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        appType = AppType(a)
        r = appType.modifyAppType(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppType', 'modifyAppType', body)

    def testDeleteAppType(self):
        a = Auth(username, pwd)
        body = {
            'type_uuids': ['2E27351F-720E-EA77-C0A6-7D769D7CADB1'],
        }
        
        appType = AppType(a)
        r = appType.deleteAppType(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppType', 'deleteAppType', body)


if __name__ == '__main__':
    unittest.main()
