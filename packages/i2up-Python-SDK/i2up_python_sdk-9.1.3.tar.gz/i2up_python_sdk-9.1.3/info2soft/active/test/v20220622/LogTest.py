
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.active.v20220622.Log import Log
# from info2soft.active.v20200722.Log import Log
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


class LogTestCase(unittest.TestCase):

    def testListLogWarning(self):
        a = Auth(username, pwd)
        body = {
            'limit': 1,
            'offset': '',
        }
        
        log = Log(a)
        r = log.listLogWarning(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Log', 'listLogWarning', body)

    def testListRuleLog(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'date_start': '',
            'date_end': '',
            'type': 1,
            'module_type': 1,
            'query_type': 1,
        }

        log = Log(a)
        r = log.listRuleLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Log', 'listRuleLog', body)


if __name__ == '__main__':
    unittest.main()
