
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.common.CompareResult import CompareResult
# from info2soft.common.v20200722.CompareResult import CompareResult
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


class CompareResultTestCase(unittest.TestCase):

    def testListCompareResult(self):
        a = Auth(username, pwd)
        body = {
            'page': '',
            'limit': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        compareResult = CompareResult(a)
        r = compareResult.listCompareResult(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'CompareResult', 'listCompareResult', body)

    def testOperateCompareResult(self):
        a = Auth(username, pwd)
        body = {
            'result_uuids': [],
            'operate': '',
        }
        
        compareResult = CompareResult(a)
        r = compareResult.operateCompareResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'CompareResult', 'operateCompareResult', body)

    def testDeleteCompareResult(self):
        a = Auth(username, pwd)
        body = {
            'result_uuids': [],
        }
        
        compareResult = CompareResult(a)
        r = compareResult.deleteCompareResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'CompareResult', 'deleteCompareResult', body)

    def testViewConfig(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        compareResult = CompareResult(a)
        r = compareResult.viewConfig(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'CompareResult', 'viewConfig', body)

    def testListDiffDetail(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'type': '',
            'page': 1,
            'limit': 10,
        }

        compareResult = CompareResult(a)
        r = compareResult.listDiffDetail(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'CompareResult', 'listDiffDetail', body)


if __name__ == '__main__':
    unittest.main()
